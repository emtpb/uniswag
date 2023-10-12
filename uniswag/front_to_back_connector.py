import csv
import os
import threading
import time

from PySide6 import QtCore, QtCharts
from PySide6.QtCore import QPointF
from PySide6.QtGui import QColor
from PySide6.QtQuick import QQuickItemGrabResult

from uniswag.device_manager import DeviceManager
from uniswag.devices.oscilloscopes.math_osc import MathOsc


# noinspection PyCallingNonCallable
class FrontToBackConnector(QtCore.QObject):

    # various signals to trigger mostly (but not exclusively) frontend functions
    addToDeviceList = QtCore.Signal('QVariantMap', list)
    removeFromDeviceList = QtCore.Signal('QVariantMap', bool)
    addChannelToDevice = QtCore.Signal('QVariantMap', 'QVariantMap')
    removeChannelFromDevice = QtCore.Signal('QVariantMap', 'QVariantMap')
    selectedDeviceUpdated = QtCore.Signal('QVariantMap')
    selectedChannelUpdated = QtCore.Signal('QVariantMap', int)
    enabledChannelsUpdated = QtCore.Signal('QVariantMap', list)
    reloadMathChProp = QtCore.Signal('QVariantMap', int)
    addSeries = QtCore.Signal(QColor)
    isRunning = QtCore.Signal('QVariantMap', bool)

    def __init__(self):
        """
        The main interface connecting front- to backend, inheriting from QtCore.QObject.

        QT signals are used to invoke frontend methods and QT slots to expose backend methods.

        Returns:
            FrontToBackConnector:
                A FrontToBackConnector object.
        """
        super(FrontToBackConnector, self).__init__()

        # the diagram that displays all devices' measurement data
        self.norm_chart = None
        self.norm_x_axis = None
        self.norm_y_axis = None
        # the root-series needs to remain intact
        # ("series" objects can hold a series of data points)
        self.norm_series = None
        # the current X axis limits (minimum and maximum value) of the measurement data chart
        self._norm_x_axis_range = [0.0, 1.0]
        # the current Y axis limits (minimum and maximum value) of the measurement data chart
        self._norm_y_axis_range = [0.0, 1.0]
        # an indicator for whether the X and Y axis limits should be set on the next measurement data chart updates
        self._update_norm_chart_axes = True

        # the diagram that displays all devices' FFT data
        self.fft_chart = None
        self.fft_x_axis = None
        self.fft_y_axis = None
        # the root-series needs to remain intact
        # ("series" objects can hold a series of data points)
        self.fft_series = None
        # the current X axis limits (minimum and maximum value) of the FFT data chart
        self._fft_x_axis_range = [0.0, 1.0]
        # the current Y axis limits (minimum and maximum value) of the FFT data chart
        self._fft_y_axis_range = [0.0, 1.0]
        # an indicator for whether the X and Y axis limits should be set on the next FFT data chart updates
        self._update_fft_chart_axes = True

        # a percentual value of the current X/Y axis limits of the raw measurement/FFT chart which determines,
        # how much smaller the respective graph's values can become before the axis limits are adjusted
        self._axis_range_tolerance = 0.1

        # the series of the diagram that displays the currently selected device's generated signal
        # ("series" objects can hold a series of data points)
        self.preview_series = None
        self.preview_x_axis = None
        self.preview_y_axis = None

        # the device to which any oscilloscope settings are currently applied
        self.selected_osc = None
        # the device to which any generator settings are currently applied
        self.selected_gen = None
        # the channel (of the currently selected oscilloscope) to which any oscilloscope settings are currently applied
        self.selected_osc_ch = None
        # the channel (of the currently selected generator) to which any generator settings are currently applied
        self.selected_gen_ch = None

        # a data structure that gives easy access to all currently enabled channels across all oscilloscopes
        self._visible_oscs = {}

        # locks the ability to change the currently selected oscilloscope
        self._mutex_osc_selection = threading.Lock()
        # locks the ability to change the currently selected generator
        self._mutex_gen_selection = threading.Lock()
        # locks the ability to change the currently selected oscilloscope channel
        self._mutex_osc_ch_selection = threading.Lock()
        # locks the ability to change the currently selected generator channel
        self._mutex_gen_ch_selection = threading.Lock()
        # locks the ability to change the currently enabled channels across all oscilloscopes
        self._mutex_osc_visibility = threading.Lock()
        # locks the ability to change the currently enabled channels across all generators
        self._mutex_gen_output = threading.Lock()
        # prevents the indicator, for whether the axis-limits of the measurement data chart should be updated,
        # from being accessed by multiple threads concurrently
        self._mutex_norm_chart_axes_update = threading.Lock()
        # prevents the indicator, for whether the axis-limits of the FFT data chart should be updated,
        # from being accessed by multiple threads concurrently
        self._mutex_fft_chart_axes_update = threading.Lock()
        # prevents the series of the diagram that displays the currently selected device's generated signal
        # from being accessed by multiple threads concurrently
        self._mutex_preview_series = threading.Lock()

        # blocks device list updates in frontend
        self._blocker_device_list_update = threading.Lock()
        self._blocker_device_list_update.acquire()

        # emitting this signal will trigger the connected slot's function
        self.addSeries.connect(self._on_add_series)
        # a barrier that waits for the connected slot's function to complete
        # after the corresponding signal has been emitted
        self._barrier_series_addition = threading.Barrier(2)
        # a tuple of the two newest series that have been added to the chart by the connected slot's function
        # (this attribute is used to share information inbetween threads)
        self._latest_series = None

        # the device manager provides access to the currently connected devices
        self._devices = DeviceManager(self._device_list_update, self._device_stopped)

        # safeguards file system checks for the "uniswag_exports" folder
        self._mutex_file_system_manipulation = threading.Lock()
        # a list of non-alphanumeric characters that are allowed for use in the file names of exported measurement data
        self._allowed_file_name_chars = [' ', '&', '(', ')', '=', '+', '~', '#', ',', ';', '-', '_']

    def _get_file_prefix(self):
        """
        Returns a string that represents the absolute file path to the "uniswag_exports" folder
        concatenated with the current date & time.

        If the "uniswag_exports" folder does not exist,
        it will be automatically created in the current working directory.

        Returns:
            str:
                The file prefix with the following format:
                CurrentWorkingDirectory/uniswag_exports/Date_Time
        """
        current_date = time.strftime('%Y-%m-%d_%H-%M-%S')
        target_directory = os.path.join(os.getcwd(), 'uniswag_exports')
        prefix = os.path.join(target_directory, current_date)

        # create target directory (if not already existent)
        self._mutex_file_system_manipulation.acquire()
        if not os.path.exists(target_directory):
            os.mkdir(target_directory)
        self._mutex_file_system_manipulation.release()

        return prefix

    @QtCore.Slot()
    def save_as_csv(self):
        """
        Saves the data points currently visible in the oscilloscope measurement and FFT charts to CSV files.

        The actual process of writing data to file is delegated to a separate thread.
        """
        thread = threading.Thread(target=self._save_as_csv_thread, daemon=True)
        thread.start()

    def _save_as_csv_thread(self):
        """
        Saves the data points currently visible in the oscilloscope measurement and FFT charts to CSV files.

        One file per graph, with the file name format being the following:
        Date_Time_DeviceID_ChannelNumber_GraphType.csv
        Blocks chart updates and oscilloscope channel enabling/disabling during execution (and vice versa).
        """
        # define the file prefix (first part of the file name) based on the current date/time and absolute file path
        file_prefix = self._get_file_prefix()

        # iterate through all oscilloscopes where at least 1 channel is set to "visible"
        self._mutex_osc_visibility.acquire()
        for visible_osc in self._visible_oscs.values():

            # get the Oscilloscope object and retrieve its measurement data
            device = visible_osc['Device']
            retrieved_vals = device.retrieve()

            # get the oscilloscope's ID
            device_id_raw = device.id['Vendor'] + '_' + device.id['Name'] + '_' + device.id['SerNo']
            device_id = ''
            for character in device_id_raw:
                if character.isalnum() or character in self._allowed_file_name_chars:
                    device_id += character
                else:
                    device_id += '_'

            # iterate through measurement data by channels
            for channel_data in retrieved_vals['Points'].items():

                # get the channel number
                channel_no = str(channel_data[0])

                # the first graph in a channel's data set is always the raw measurement data
                graph_type = 'Norm'

                # iterate through the channel data by graphs (raw measurement graph & FFT graph)
                for data_list in channel_data[1]:

                    # create and open a separate file per graph
                    file_name = file_prefix + '_' + device_id + '_' + channel_no + '_' + graph_type
                    with open(file_name + '.csv', 'w') as opened_file:
                        csv_w = csv.writer(opened_file)

                        # CSV header
                        csv_w.writerow(['X', 'Y'])

                        # write every single point contained in the graph to the file
                        for data_point in data_list:
                            csv_w.writerow([data_point.x(), data_point.y()])

                    # the next graph in the channel's data set is the FFT graph
                    graph_type = 'FFT'

        self._mutex_osc_visibility.release()

    @QtCore.Slot(QQuickItemGrabResult)
    def save_as_png(self, image):
        """
        Saves the oscilloscope measurement chart to a PNG file.

        The actual process of writing data to file is delegated to a separate thread.

        Args:
            image (PySide6.QtQuick.QQuickItemGrabResult.QQuickItemGrabResult):
                The image captured from the oscilloscope measurement chart which will be saved in an external file.
        """
        thread = threading.Thread(target=self._save_as_png_thread, args=[image], daemon=True)
        thread.start()

    def _save_as_png_thread(self, image):
        """
        Saves the oscilloscope measurement chart to a PNG file.

        The file name format is as following:
        Date_Time.png

        The process generally fails if the "uniswag_exports" folder does not exist yet
        due to an apparently faulty scope implementation in PySide.

        Args:
            image (PySide6.QtQuick.QQuickItemGrabResult.QQuickItemGrabResult):
                The image captured from the oscilloscope measurement chart which will be saved in an external file.
        """
        file_name = self._get_file_prefix()
        try:
            image.saveToFile(file_name + '.png')
        except RuntimeError:
            print('Could not export as PNG, please try again.\n'
                  'This issue was most likely caused by the "uniswag_exports" folder not being created in time.')

    @QtCore.Slot(QtCharts.QAbstractSeries, QtCharts.QValueAxis, QtCharts.QValueAxis)
    def init_norm_chart(self, series, x_axis, y_axis):
        """
        Initializes the measurement data chart.

        The root-series is saved in a class attribute, as well as its chart and the passed chart axes.
        Additionally, all other existing series belonging to the chart are removed.

        Args:
            series (PySide6.QtCharts.QAbstractSeries.QAbstractSeries):
                The root-series on which the chart is based.
            x_axis (PySide6.QtCharts.QValueAxis.QValueAxis):
                The X axis to be used in the chart.
            y_axis (PySide6.QtCharts.QValueAxis.QValueAxis):
                The Y axis to be used in the chart.
        """
        self.norm_series = series
        self.norm_chart = series.chart()
        self.norm_chart.removeAllSeries()
        self.norm_x_axis = x_axis
        self.norm_x_axis.setRange(0, 1)
        self.norm_y_axis = y_axis
        self.norm_y_axis.setRange(0, 1)

    @QtCore.Slot(QtCharts.QAbstractSeries, QtCharts.QValueAxis, QtCharts.QValueAxis)
    def init_fft_chart(self, series, x_axis, y_axis):
        """
        Initializes the FFT data chart.

        The root-series is saved in a class attribute, as well as its chart and the passed chart axes.
        Additionally, all other existing series belonging to the chart are removed.

        Args:
            series (PySide6.QtCharts.QAbstractSeries.QAbstractSeries):
                The root-series on which the chart is based.
            x_axis (PySide6.QtCharts.QValueAxis.QValueAxis):
                The X axis to be used in the chart.
            y_axis (PySide6.QtCharts.QValueAxis.QValueAxis):
                The Y axis to be used in the chart.
        """
        self.fft_series = series
        self.fft_chart = series.chart()
        self.fft_chart.removeAllSeries()
        self.fft_x_axis = x_axis
        self.fft_y_axis = y_axis

    @QtCore.Slot(QtCharts.QAbstractSeries, QtCharts.QValueAxis, QtCharts.QValueAxis)
    def init_signal_preview_chart(self, series, x_axis, y_axis):
        """
        Initializes the chart displaying the currently generated signal.

        The chart includes exactly one series object, which stores the data points that result in the signal graph.
        This series is reused everytime the signal preview is updated.

        Args:
            series (PySide6.QtCharts.QAbstractSeries.QAbstractSeries):
                The series which will store the generated waveform data points.
            x_axis (PySide6.QtCharts.QValueAxis.QValueAxis):
                The X axis to be used in the chart.
            y_axis (PySide6.QtCharts.QValueAxis.QValueAxis):
                The Y axis to be used in the chart.
        """
        self.preview_series = series
        self.preview_x_axis = x_axis
        self.preview_y_axis = y_axis

    def start_device_list_updates(self):
        """
        Once called, notifications to frontend about changes in the device list are enabled.
        """
        self._blocker_device_list_update.release()

    def _device_list_update(self, event, changed_devices):
        """
        Notifies frontend about changes to the device list
        (and resets the currently selected device & channel if necessary).

        The IDs of the added/removed devices are each passed individually to frontend
        and, depending on the type of update, either the respective device's channel IDs or
        a boolean indicating whether the device was currently selected at the time of removal.
        This function will block until another function designated to
        starting the device list updates has been called once.

        Args:
            event (str):
                "add" if the devices were added to the device list,
                "remove" if they were removed.
            changed_devices (list[uniswag.devices.device.Device]):
                The list of devices that were afflicted by the given event.
        """
        self._blocker_device_list_update.acquire()

        # check if devices were added to the device list
        if event == 'add':
            for device in changed_devices:

                # create a list of the device's channel IDs
                channel_list = []
                for c in device.ch:
                    channel_list.append(c.id)

                # pass the added device's ID and its channel ID list to frontend
                self.addToDeviceList.emit(device.id, channel_list)

        # check if devices were removed from the device list
        else:
            for device in changed_devices:

                # indicates whether the removed device was the selected one
                sel_dev_removed = False

                # reset the selected oscilloscope to "None" if it was removed
                if self.selected_osc is not None:
                    self._mutex_osc_selection.acquire()
                    if self.selected_osc.id == device.id:
                        self.selected_osc = None
                        sel_dev_removed = True
                    self._mutex_osc_selection.release()

                # reset the selected oscilloscope channel to "None" if the associated device was removed
                if sel_dev_removed:
                    self._mutex_osc_ch_selection.acquire()
                    self.selected_osc_ch = None
                    self._mutex_osc_ch_selection.release()

                # reset the selected generator to "None" if it was removed
                else:
                    if self.selected_gen is not None:
                        self._mutex_gen_selection.acquire()
                        if self.selected_gen.id == device.id:
                            self.selected_gen = None
                            sel_dev_removed = True
                        self._mutex_gen_selection.release()

                    # reset the selected generator channel to "None" if the associated device was removed
                    if sel_dev_removed:
                        self._mutex_gen_ch_selection.acquire()
                        self.selected_gen_ch = None
                        self._mutex_gen_ch_selection.release()

                # remove all remaining graphs that correspond to the removed device's channels
                self._mutex_osc_visibility.acquire()
                visible_device = self._visible_oscs.get(frozenset(device.id.values()))
                if visible_device is not None:
                    for ch in visible_device['Channels']:
                        self.norm_chart.removeSeries(ch['Norm series'])
                        self.fft_chart.removeSeries(ch['FFT series'])
                    self._visible_oscs.pop(frozenset(device.id.values()))
                self._mutex_osc_visibility.release()

                # pass the removed device's ID and an indicator (whether it was selected) to frontend
                self.removeFromDeviceList.emit(device.id, sel_dev_removed)

        self._reload_math_ch_properties()

        self._blocker_device_list_update.release()

    def channel_list_update(self, event, changed_device, changed_channel_id):
        """
        Notifies frontend about changes to the channel list of the specified oscilloscope
        (and switches the currently selected channel if necessary).

        The IDs of both the oscilloscope and the channel are passed to frontend.
        This function will block until another function designated to
        starting the device list updates has been called once.

        Args:
            event (str):
                "add" if an entry was added to the device's channel list,
                "remove" if an entry was removed.
            changed_device (uniswag.devices.device.Device):
                The device that either gained or lost one channel.
            changed_channel_id (dict[str, Any]):
                The ID of the added/removed channel.
        """
        self._blocker_device_list_update.acquire()

        # check if a channel was added to the device's channel list
        if event == 'add':

            # pass the device's and channel's ID to frontend
            self.addChannelToDevice.emit(changed_device.id, changed_channel_id)

        # check if a channel was removed to the device's channel list
        else:

            # matches the currently selected oscilloscope, but only if it is equal to the changed device
            sel_osc = None
            # if the removed oscilloscope channel was the selected one, this will match the new selected channel
            new_sel_ch = None

            # find out if the currently selected oscilloscope corresponds to the changed device
            if self.selected_osc is not None:
                self._mutex_osc_selection.acquire()
                if self.selected_osc.id == changed_device.id:
                    sel_osc = self.selected_osc
                self._mutex_osc_selection.release()

            # update the currently selected oscilloscope channel if it was removed
            if sel_osc is not None:
                self._mutex_osc_ch_selection.acquire()
                if self.selected_osc_ch.id == changed_channel_id:

                    # fall back to the first channel; prioritize the channel anterior to the selected one
                    new_sel_ch = sel_osc.ch[0]
                    for c in sel_osc.ch:
                        if c.id['No'] == changed_channel_id['No'] - 1:
                            new_sel_ch = c
                            break
                    self.selected_osc_ch = new_sel_ch

                self._mutex_osc_ch_selection.release()

            # pass the device's and channel's ID to frontend
            self.removeChannelFromDevice.emit(changed_device.id, changed_channel_id)

            # pass the device's ID and the updated selected channel number to frontend
            if new_sel_ch is not None:
                self.selectedChannelUpdated.emit(changed_device.id, new_sel_ch.id['No'])

        self._reload_math_ch_properties()

        self._blocker_device_list_update.release()

    def _reload_math_ch_properties(self):
        """
        Notifies frontend that the currently displayed property values of the selected math oscilloscope channel
        are no longer up to date and need to be reloaded.

        After updating the device list (or updating the channel count of a specific device) the math oscilloscope's
        currently set operands as well as the list of available operands are automatically updated in backend.
        Frontend however needs to be notified about this change by invoking this function.
        No signal will be emitted to frontend if the math oscilloscope is not selected one during invocation.
        """
        # check if the currently selected oscilloscope happens to be the MathOsc
        selected_math_osc = None
        self._mutex_osc_selection.acquire()
        if isinstance(self.selected_osc, MathOsc):
            selected_math_osc = self.selected_osc
        self._mutex_osc_selection.release()

        # if the Math Osc is indeed the currently selected oscilloscope,
        # the selected channel's property values are reloaded in frontend
        if selected_math_osc is not None:
            self._mutex_osc_ch_selection.acquire()
            self.reloadMathChProp.emit(selected_math_osc.id, self.selected_osc_ch.id['No'])
            self._mutex_osc_ch_selection.release()

    @QtCore.Slot(bool)
    def norm_chart_axes_updates(self, enable):
        """
        Determines, whether the X and Y axis limits should be set on the next measurement data chart updates.

        Args:
            enable (bool):
                "True" will automatically resize the chart to properly display the entirety of every graph,
                "False" will keep the current detail.
        """
        self._mutex_norm_chart_axes_update.acquire()
        self._update_norm_chart_axes = enable
        self._mutex_norm_chart_axes_update.release()

    @QtCore.Slot(bool)
    def fft_chart_axes_updates(self, enable):
        """
        Determines, whether the X and Y axis limits should be set on the next FFT data chart updates.

        Args:
            enable (bool):
                "True" will automatically resize the chart to properly display the entirety of every graph,
                "False" will keep the current detail.
        """
        self._mutex_fft_chart_axes_update.acquire()
        self._update_fft_chart_axes = enable
        self._mutex_fft_chart_axes_update.release()

    @QtCore.Slot()
    def start_chart_updates(self):
        """
        Starts a thread dedicated to continuously update the graphs in the measurement and FFT data charts.
        """
        thread = threading.Thread(target=self._chart_update_thread, daemon=True)
        thread.start()

    def _chart_update_thread(self):
        """
        Continuously updates the graphs in the measurement and FFT data charts.

        Measurement data is retrieved from every oscilloscope that has at least one enabled channel.
        Each graph in a chart is updated according to the data
        (provided that the data has changed since the last update).
        Optionally, the graph axis limits are set to the smallest resp. biggest overall data value.
        """
        while True:
            time.sleep(0.05)
            norm_x_min = norm_x_max = norm_y_min = norm_y_max = None
            fft_x_min = fft_x_max = fft_y_min = fft_y_max = None

            # iterate through all oscilloscopes where at least 1 channel is set to "visible"
            self._mutex_osc_visibility.acquire()
            for obj in self._visible_oscs.values():

                # get the Oscilloscope object, retrieve its values and check whether there is new data
                device = obj['Device']
                retrieved_vals = device.retrieve(True)
                if retrieved_vals['New']:

                    # replace all data points in the respective channel's graph with the new data points
                    for channel_data in retrieved_vals['Points'].items():

                        ch_no = channel_data[0]
                        data_points_norm = channel_data[1][0]
                        data_points_fft = channel_data[1][1]

                        # ensure that the channel to which the data belongs to is still enabled
                        if device.ch[ch_no - 1].is_enabled:

                            current_channel = next(channel for channel in obj['Channels'] if channel['No'] == ch_no)

                            current_channel['Norm series'].replace(data_points_norm)
                            current_channel['FFT series'].replace(data_points_fft)

                # get the new X and Y axis limits
                lim_time = retrieved_vals['Norm limits']['Time']
                lim_voltage = retrieved_vals['Norm limits']['Voltage']
                norm_x_min = min(norm_x_min, lim_time[0]) if norm_x_min is not None else lim_time[0]
                norm_x_max = max(norm_x_max, lim_time[1]) if norm_x_max is not None else lim_time[1]
                norm_y_min = min(norm_y_min, lim_voltage[0]) if norm_y_min is not None else lim_voltage[0]
                norm_y_max = max(norm_y_max, lim_voltage[1]) if norm_y_max is not None else lim_voltage[1]
                lim_frequency = retrieved_vals['FFT limits']['Frequency']
                lim_share = retrieved_vals['FFT limits']['Share']
                fft_x_min = min(fft_x_min, lim_frequency[0]) if fft_x_min is not None else lim_frequency[0]
                fft_x_max = max(fft_x_max, lim_frequency[1]) if fft_x_max is not None else lim_frequency[1]
                fft_y_min = min(fft_y_min, lim_share[0]) if fft_y_min is not None else lim_share[0]
                fft_y_max = max(fft_y_max, lim_share[1]) if fft_y_max is not None else lim_share[1]
            self._mutex_osc_visibility.release()

            # determine whether the new X and Y axis limits should be set
            self._mutex_norm_chart_axes_update.acquire()
            update_norm_axes = self._update_norm_chart_axes
            self._mutex_norm_chart_axes_update.release()
            self._mutex_fft_chart_axes_update.acquire()
            update_fft_axes = self._update_fft_chart_axes
            self._mutex_fft_chart_axes_update.release()

            # apply the new X and Y axis limits
            if all([update_norm_axes,
                    norm_x_min is not None, norm_x_max is not None, norm_y_min is not None, norm_y_max is not None]):
                self._set_chart_axis_limits('Norm', norm_x_min, norm_x_max, norm_y_min, norm_y_max)
            if all([update_fft_axes,
                    fft_x_min is not None, fft_x_max is not None, fft_y_min is not None, fft_y_max is not None]):
                self._set_chart_axis_limits('FFT', fft_x_min, fft_x_max, fft_y_min, fft_y_max)

    def _set_chart_axis_limits(self, chart_type, x_min, x_max, y_min, y_max):
        """
        Sets the minimum and maximum values for the X and Y axis of the specified chart.

        Only updates an axis value if it is not within the tolerance range
        (reduces the frequency of axis updates).

        Args:
            chart_type (str):
                The chart whose axes are to be updated.
                "Norm" for the raw measurement data chart, "FFT" for the FFT data chart.
            x_min (float):
                The lower limit of the X axis.
            x_max (float):
                The upper limit of the X axis.
            y_min (float):
                The lower limit of the Y axis.
            y_max (float):
                The upper limit of the Y axis.
        """
        # get the chart's current axis limits
        if chart_type == 'Norm':
            x_axis_range = self._norm_x_axis_range
            y_axis_range = self._norm_y_axis_range
        else:
            x_axis_range = self._fft_x_axis_range
            y_axis_range = self._fft_y_axis_range

        # calculate whether the new axis limits should replace the current ones

        if x_axis_range[0] != 0:
            if x_min > x_axis_range[0] * (
                    1 + self._axis_range_tolerance * ((-1 * x_axis_range[0]) / (-1 * abs(x_axis_range[0])))) \
                    or x_min < x_axis_range[0]:
                x_axis_range[0] = x_min
        else:
            if x_min != x_axis_range[0]:
                x_axis_range[0] = x_min

        if x_axis_range[1] != 0:
            if x_max < x_axis_range[1] * (
                    1 - self._axis_range_tolerance * ((-1 * x_axis_range[1]) / (-1 * abs(x_axis_range[1])))) \
                    or x_max > x_axis_range[1]:
                x_axis_range[1] = x_max
        else:
            if x_max != x_axis_range[1]:
                x_axis_range[1] = x_max

        if y_axis_range[0] != 0:
            if y_min > y_axis_range[0] * (
                    1 + self._axis_range_tolerance * ((-1 * y_axis_range[0]) / (-1 * abs(y_axis_range[0])))) \
                    or y_min < y_axis_range[0]:
                y_axis_range[0] = y_min
        else:
            if y_min != y_axis_range[0]:
                y_axis_range[0] = y_min

        if y_axis_range[1] != 0:
            if y_max < y_axis_range[1] * (
                    1 - self._axis_range_tolerance * ((-1 * y_axis_range[1]) / (-1 * abs(y_axis_range[1])))) \
                    or y_max > y_axis_range[1]:
                y_axis_range[1] = y_max
        else:
            if y_max != y_axis_range[1]:
                y_axis_range[1] = y_max

        # update the chart's current axis limits
        if chart_type == 'Norm':
            self._norm_x_axis_range = x_axis_range
            self._norm_y_axis_range = y_axis_range
            self.norm_x_axis.setRange(self._norm_x_axis_range[0], self._norm_x_axis_range[1])
            self.norm_y_axis.setRange(self._norm_y_axis_range[0], self._norm_y_axis_range[1])
        else:
            self._fft_x_axis_range = x_axis_range
            self._fft_y_axis_range = y_axis_range
            self.fft_x_axis.setRange(self._fft_x_axis_range[0], self._fft_x_axis_range[1])
            self.fft_y_axis.setRange(self._fft_y_axis_range[0], self._fft_y_axis_range[1])

    def update_signal_preview(self, device_id, channel):
        """
        Updates the graph in the signal preview chart to display the specified channel's generated waveform.

        The update will only be carried out if the passed device ID and channel object
        match the currently selected device & channel.

        Args:
            device_id (dict[str, str]):
                The ID of the device to which the channel belongs.
            channel (uniswag.devices.generator.GenChannel):
                The channel that generates the signal which is to be displayed by the chart.
        """
        # whether the chart axis limits should be updated
        update_x_axis = False
        update_y_axis = False

        # get the graph's new X and Y values
        time_vector, voltage_vector = channel.get_signal_preview()
        x_min = min(time_vector)
        x_max = max(time_vector)
        y_min = min(voltage_vector)
        y_max = max(voltage_vector)
        if x_min != x_max:
            update_x_axis = True
        if y_min != y_max:
            update_y_axis = True

        # combine each element from the time and voltage vector into a QPoint
        generated_waveform = [QPointF(time_vector[i], voltage_vector[i]) for i in range(len(time_vector))]

        self._mutex_gen_ch_selection.acquire()
        selected_channel = self.selected_gen_ch
        self._mutex_gen_ch_selection.release()

        self._mutex_gen_selection.acquire()
        selected_device = self.selected_gen
        self._mutex_gen_selection.release()

        # ensure that the update of the signal preview graph was issued for the currently selected generator channel
        if selected_device.id == device_id and selected_channel.id == channel.id:
            self._mutex_preview_series.acquire()
            self.preview_series.replace(generated_waveform)
            if update_x_axis:
                self.preview_x_axis.setRange(x_min, x_max)
            if update_y_axis:
                self.preview_y_axis.setRange(y_min, y_max)
            self._mutex_preview_series.release()

    @QtCore.Slot(QColor)
    def _on_add_series(self, color):
        """
        Adds two new series to the data charts, one for the measurement data and one for the FFT data.

        The newly added series are saved as a tuple in a class attribute for easy access across threads.
        At the end of the method, the threading barrier for "adding a chart series tuple" is passed.

        Args:
            color (QColor):
                The color to assign to both of the newly added series.
        """
        self._latest_series = (QtCharts.QLineSeries(self.norm_chart), QtCharts.QLineSeries(self.fft_chart))
        self._latest_series[0].setColor(color)
        self._latest_series[1].setColor(color)
        self.norm_chart.addSeries(self._latest_series[0])
        self.norm_chart.setAxisX(self.norm_x_axis, self._latest_series[0])
        self.norm_chart.setAxisY(self.norm_y_axis, self._latest_series[0])
        self.fft_chart.addSeries(self._latest_series[1])
        self.fft_chart.setAxisX(self.fft_x_axis, self._latest_series[1])
        self.fft_chart.setAxisY(self.fft_y_axis, self._latest_series[1])
        self._barrier_series_addition.wait()

    def _add_visible_osc(self, device_id, channel_no, colors):
        """
        Enables either all channels or one specific channel of the given oscilloscope.

        For each channel to be enabled, two new chart series are created (for measurement and FFT data).
        Afterwards, the passed device is added to the dictionary of visible oscilloscopes
        (oscilloscopes that have at least one channel enabled).

        Args:
            device_id (dict[str, str]):
                The oscilloscope whose channel(s) to enable.
            channel_no (int):
                The number of the channel to enable.
                If none is given, all channels will be enabled.
            colors (list[QColor]):
                A list of the colors to assign to the respective channels' graphs.
                Contains either one color (if a specific channel was enabled), or all colors of an oscilloscope.

        Returns:
            list[int]:
                The numbers of the oscilloscope's currently enabled channels.
        """
        # find the oscilloscope whose channels are to be enabled
        for device in self._devices.device_list:
            if device.id == device_id:

                enabled_channels = []
                enabled_channel_nos = []

                # enable all channels, if no specific channel number is given
                if channel_no is None:
                    for i in range(device.ch_cnt):

                        # wait for the main thread to add the new series
                        # (pass threading barrier for "adding a chart series tuple")
                        self.addSeries.emit(colors[i])
                        self._barrier_series_addition.wait()

                        # save the series and the corresponding channel number
                        enabled_channels.append({
                            'No': i + 1,
                            'Norm series': self._latest_series[0],
                            'FFT series': self._latest_series[1]
                        })

                        enabled_channel_nos.append(i + 1)

                        # enable the oscilloscope channel
                        device.ch[i].is_enabled = True

                # enable a specific channel, if the corresponding number is given
                else:

                    # wait for the main thread to add the new series
                    # (pass threading barrier for "adding a chart series tuple")
                    self.addSeries.emit(colors[0])
                    self._barrier_series_addition.wait()

                    # save the series and the corresponding channel number
                    enabled_channels.append({
                        'No': channel_no,
                        'Norm series': self._latest_series[0],
                        'FFT series': self._latest_series[1]
                    })

                    enabled_channel_nos.append(channel_no)

                    # enable the oscilloscope channel
                    device.ch[channel_no - 1].is_enabled = True

                # save the series and numbers of all enabled channels along with the oscilloscope,
                # to which they belong
                self._visible_oscs[frozenset(device_id.values())] = {
                    'Device': device,
                    'Channels': enabled_channels
                }

                return enabled_channel_nos

    def _remove_visible_osc(self, device_id):
        """
        Disables all channels of the given oscilloscope.

        All chart series linked to enabled channels are deleted in the process.
        Afterwards, the passed oscilloscope is removed from the dictionary of visible oscilloscopes
        (oscilloscopes that have at least one channel enabled).

        Args:
            device_id (dict[str, str]):
                The oscilloscope whose channels to disable.

        Returns:
            list[int]:
                The numbers of the oscilloscope's currently enabled channels.
        """
        dev = self._visible_oscs[frozenset(device_id.values())]['Device']

        # disable all the oscilloscope's channels
        for ch in dev.ch:
            ch.is_enabled = False

        # stop the oscilloscope as soon as possible
        thread = threading.Thread(target=self._device_full_stop_thread, args=[dev], daemon=True)
        thread.start()

        # remove all the series that correspond to the formerly enabled channels
        for ch in self._visible_oscs[frozenset(device_id.values())]['Channels']:
            self.norm_chart.removeSeries(ch['Norm series'])
            self.fft_chart.removeSeries(ch['FFT series'])

        self._visible_oscs.pop(frozenset(device_id.values()))

        return []

    def _update_visible_osc(self, device_id, channel_no, colors):
        """
        Either enables or disables the specified channel of the given oscilloscope.

        If the channel is currently disabled, is will be enabled, and the other way around.
        Accordingly, the corresponding chart series are either created or deleted, and
        the dictionary of visible oscilloscopes (oscilloscopes that have at least one channel enabled) is updated.

        Args:
            device_id (dict[str, str]):
                The oscilloscope whose channel(s) to toggle.
            channel_no (int):
                The number of the channel to toggle.
            colors (list[QColor]):
                A list with a single entry of the color to assign to the respective channel's graph.

        Returns:
            list[int]:
                The numbers of the oscilloscope's currently enabled channels.
        """
        # find the oscilloscope whose channels are to be enabled/disabled
        for device in self._devices.device_list:
            if device.id == device_id:
                visible_device = self._visible_oscs.get(frozenset(device_id.values()))

                # get the oscilloscope's currently enabled channels
                enabled_channels = visible_device['Channels']

                enabled_channel_nos = []
                channel_position_in_list = None

                # try to find the passed channel number in the list of enabled channels
                for i in range(len(enabled_channels)):
                    current_ch_no = enabled_channels[i]['No']
                    enabled_channel_nos.append(current_ch_no)
                    if current_ch_no == channel_no:
                        channel_position_in_list = i

                # the passed channel number needs to be enabled, if it is not already
                if channel_position_in_list is None:

                    # wait for the main thread to add the new series
                    # (pass threading barrier for "adding a chart series tuple")
                    self.addSeries.emit(colors[0])
                    self._barrier_series_addition.wait()

                    # save the series and the corresponding channel number
                    enabled_channels.append({
                        'No': channel_no,
                        'Norm series': self._latest_series[0],
                        'FFT series': self._latest_series[1]
                    })

                    enabled_channel_nos.append(channel_no)

                    # enable the oscilloscope channel
                    device.ch[channel_no - 1].is_enabled = True

                # the passed channel number needs to be disabled, if it is currently enabled
                else:

                    # disable the oscilloscope channel
                    device.ch[channel_no - 1].is_enabled = False

                    # remove the series that corresponds to the formerly enabled channel
                    self.norm_chart.removeSeries(enabled_channels[channel_position_in_list]['Norm series'])
                    self.fft_chart.removeSeries(enabled_channels[channel_position_in_list]['FFT series'])

                    del enabled_channels[channel_position_in_list]
                    if not enabled_channels:

                        # stop the oscilloscope as soon as possible
                        thread = threading.Thread(target=self._device_full_stop_thread,
                                                  args=[visible_device['Device']],
                                                  daemon=True)
                        thread.start()

                        self._visible_oscs.pop(frozenset(device_id.values()))

                    enabled_channel_nos.remove(channel_no)

                return enabled_channel_nos

    @QtCore.Slot('QVariantMap', str, list)
    def visibility_checkbox_toggled(self, device_id, channel_no, colors):
        """
        Toggles the "enabled" status of the specified channel from the given oscilloscope.

        The actual setting to the oscilloscope's channel is delegated to a separate thread.

        Args:
            device_id (dict[str, str]):
                The oscilloscope whose channel(s) to toggle.
            channel_no (int):
                The number of the channel to toggle.
                If none is given, all channels will be enabled/disabled.
            colors (list[QColor]):
                A list of the colors to assign to the respective channels' graphs.
                Contains either one color (if a specific channel was toggled), or all colors of a device.
        """
        # convert QML's NaN into Python's None if necessary, forward the parameter otherwise
        if channel_no == 'NaN':
            args = [device_id, None, colors]
        else:
            args = [device_id, int(channel_no), colors]

        thread = threading.Thread(target=self._visibility_toggled_thread, args=args, daemon=True)
        thread.start()

    def _visibility_toggled_thread(self, device_id, channel_no, colors):
        """
        Toggles the "enabled" status of the specified channel from the given oscilloscope.

        Afterwards, a list of the oscilloscope's currently enabled channels is sent to frontend.

        Args:
            device_id (dict[str, str]):
                The oscilloscope whose channel(s) to toggle.
            channel_no (int):
                The number of the channel to toggle.
                If none is given, all channels will be enabled/disabled.
            colors (list[QColor]):
                A list of the colors to assign to the respective channels' graphs.
                Contains either one color (if a specific channel was toggled), or all colors of a device.
        """
        self._mutex_osc_visibility.acquire()

        # check whether at least one of the passed oscilloscope's channels is enabled and
        # either enable or disable the channel(s) accordingly
        if frozenset(device_id.values()) not in self._visible_oscs:
            enabled_channel_nos = self._add_visible_osc(device_id, channel_no, colors)
        else:
            if channel_no is None:
                enabled_channel_nos = self._remove_visible_osc(device_id)
            else:
                enabled_channel_nos = self._update_visible_osc(device_id, channel_no, colors)

        self._mutex_osc_visibility.release()

        # pass the updated list of enabled channels (and the oscilloscope to which they belong) to frontend
        self.enabledChannelsUpdated.emit(device_id, enabled_channel_nos)

    def remove_visible_ch(self, device_id, channel_no):
        """
        Deletes the chart series corresponding to the specified oscilloscope channel.
        Afterwards, the passed channel is removed from the dictionary of visible oscilloscopes
        (oscilloscopes that have at least one channel enabled).

        Does NOT disable the channel input.

        Args:
            device_id (dict[str, str]):
                The oscilloscope to which the channel belongs.
            channel_no (int):
                The number of the channel whose chart series shall be deleted.
        """
        self._mutex_osc_visibility.acquire()

        visible_device = self._visible_oscs.get(frozenset(device_id.values()))
        if visible_device is not None:

            # get the oscilloscope's currently enabled channels
            enabled_channels = visible_device['Channels']

            # try to find the passed channel number in the list of enabled channels
            channel_position_in_list = None
            for i in range(len(enabled_channels)):
                current_ch_no = enabled_channels[i]['No']
                if current_ch_no == channel_no:
                    channel_position_in_list = i

            if channel_position_in_list is not None:

                # remove the series that corresponds to the formerly enabled channel
                self.norm_chart.removeSeries(enabled_channels[channel_position_in_list]['Norm series'])
                self.fft_chart.removeSeries(enabled_channels[channel_position_in_list]['FFT series'])

                del enabled_channels[channel_position_in_list]
                if not enabled_channels:
                    # stop the oscilloscope as soon as possible
                    thread = threading.Thread(target=self._device_full_stop_thread,
                                              args=[visible_device['Device']],
                                              daemon=True)
                    thread.start()

                    self._visible_oscs.pop(frozenset(device_id.values()))

        self._mutex_osc_visibility.release()

    @QtCore.Slot('QVariantMap', str)
    def output_checkbox_toggled(self, device_id, channel_no):
        """
        Toggles the "enabled" status of the specified channel from the given generator.

        The actual setting to the generator's channel is delegated to a separate thread.

        Args:
            device_id (dict[str, str]):
                The generator whose channel(s) to toggle.
            channel_no (int):
                The number of the channel to toggle.
                If none is given, all channels will be enabled/disabled.
        """
        # convert QML's NaN into Python's None if necessary, forward the parameter otherwise
        if channel_no == 'NaN':
            args = [device_id, None]
        else:
            args = [device_id, int(channel_no)]

        thread = threading.Thread(target=self._output_toggled_thread, args=args, daemon=True)
        thread.start()

    def _output_toggled_thread(self, device_id, channel_no):
        """
        Toggles the "enabled" status of the specified channel from the given generator.

        Afterwards, a list of the generator's currently enabled channels is sent to frontend.

        Args:
            device_id (dict[str, str]):
                The generator whose channel(s) to toggle.
            channel_no (int):
                The number of the channel to toggle.
                If none is given, all channels will be enabled/disabled.
        """
        # find the generator whose channels are to be enabled/disabled
        for dev in self._devices.device_list:
            if dev.id == device_id:
                device = dev
                enabled_channel_nos = []

                self._mutex_gen_output.acquire()

                # case: no channel number was provided
                if channel_no is None:

                    # disable all channels if at least one of them was enabled
                    if any([channel.is_enabled for channel in device.ch]):
                        for channel in device.ch:
                            channel.is_enabled = False
                            if channel.is_enabled:
                                enabled_channel_nos.append(channel.id['No'])

                        # stop the generator if no channel is enabled anymore
                        if not enabled_channel_nos:
                            thread = threading.Thread(target=self._device_full_stop_thread, args=[device], daemon=True)
                            thread.start()

                    # enable all channels otherwise
                    else:
                        for channel in device.ch:
                            channel.is_enabled = True
                            if channel.is_enabled:
                                enabled_channel_nos.append(channel.id['No'])

                # case: a specific channel number was provided
                else:

                    for channel in device.ch:
                        if channel.id['No'] == channel_no:
                            # toggle the specified channel
                            channel.is_enabled = not channel.is_enabled
                        if channel.is_enabled:
                            enabled_channel_nos.append(channel.id['No'])

                    if not enabled_channel_nos:
                        # stop the generator if no channel is enabled anymore
                        thread = threading.Thread(target=self._device_full_stop_thread, args=[device], daemon=True)
                        thread.start()

                self._mutex_gen_output.release()

                # pass the updated list of enabled channels (and the generator to which they belong) to frontend
                self.enabledChannelsUpdated.emit(device_id, enabled_channel_nos)

    @QtCore.Slot('QVariantMap')
    def set_selected_device(self, device_id):
        """
        Sets the specified device as the currently selected one.

        Any device settings made in frontend are always applied to the currently selected device.

        Args:
            device_id (dict[str, str]):
                The device that has been selected.
        """
        # find the device that was selected in frontend
        for device in self._devices.device_list:
            if device.id == device_id:

                if device_id['DevType'] == 'Osc':
                    self._mutex_osc_selection.acquire()
                    self.selected_osc = device
                    self._mutex_osc_selection.release()
                elif device_id['DevType'] == 'Gen':
                    self._mutex_gen_selection.acquire()
                    self.selected_gen = device
                    self._mutex_gen_selection.release()

                # confirm selection to frontend
                self.selectedDeviceUpdated.emit(device.id)

                break

    @QtCore.Slot('QVariantMap', int)
    def set_selected_channel(self, device_id, channel_no):
        """
        Sets the specified channel of the given device as the currently selected one.

        Any channel settings made in frontend are always applied to the currently selected channel.

        Args:
            device_id (dict[str, str]):
                The device to which the selected channel belongs.
            channel_no (int):
                The number of the channel that has been selected.
        """
        if device_id['DevType'] == 'Osc':
            self._mutex_osc_selection.acquire()
            selected_device = self.selected_osc
            self._mutex_osc_selection.release()
        elif device_id['DevType'] == 'Gen':
            self._mutex_gen_selection.acquire()
            selected_device = self.selected_gen
            self._mutex_gen_selection.release()
        else:
            selected_device = None

        # ensure that the channel, which was selected in frontend, belongs to the currently selected device
        if selected_device is not None and selected_device.id == device_id:

            # find the channel
            for channel in selected_device.ch:
                if channel.id['No'] == channel_no:

                    if device_id['DevType'] == 'Osc':
                        self._mutex_osc_ch_selection.acquire()
                        self.selected_osc_ch = channel
                        self._mutex_osc_ch_selection.release()
                    elif device_id['DevType'] == 'Gen':
                        self._mutex_gen_ch_selection.acquire()
                        self.selected_gen_ch = channel
                        self._mutex_gen_ch_selection.release()

                        # update the signal preview chart when changing the selected generator channel
                        thread = threading.Thread(target=self.update_signal_preview,
                                                  args=[device_id, channel],
                                                  daemon=True)
                        thread.start()

                    # confirm selection to frontend
                    self.selectedChannelUpdated.emit(selected_device.id, channel_no)

                    break

    def _device_stopped(self, device_id):
        """
        Informs frontend about the specified device being currently NOT running.

        Used as a callback function by oscilloscopes to notify when their measurement was stopped.
        That way, frontend can react to a device stopping by itself (without a manual "stop" function call).

        Args:
            device_id (dict[str, str]):
                The ID of the device that will be stated as "not running".
        """
        self.isRunning.emit(device_id, False)

    def _device_full_stop_thread(self, device):
        """
        Stops the specified device.

        Prints a message to console, whether the stopping process was successful.
        Furthermore, frontend receives the device's ID as well as a boolean indicating if it is still running.

        Args:
            device (uniswag.devices.device.Device):
                The device to stop.
        """
        dev_id = device.id['Vendor'] + ' ' + device.id['Name'] + ' (' + device.id['SerNo'] + ')'

        success = device.stop()
        if success:
            print(dev_id + ' stopped')
        else:
            print('Could not stop ' + dev_id)

        result = device.is_running
        self.isRunning.emit(device.id, result)

    def access_osc_property(self, callback, value=None):
        """
        Invokes the specified function with the currently selected oscilloscope and the given value as parameters.

        This method is used to apply any desired setting to the currently selected oscilloscope.
        However, the actual function call and the ensuing setting to the device is delegated to a separate thread.

        Args:
            callback (function):
                The function to call in a separate thread.
            value (str):
                The (optional) second parameter to pass to the callback function.
        """
        self._mutex_osc_selection.acquire()
        device = self.selected_osc
        self._mutex_osc_selection.release()

        # convert QML's NaN (or empty String) into Python's None if necessary, forward the parameter otherwise
        if value is None:
            args = [device]
        elif value == 'NaN' or value == '':
            args = [device, None]
        else:
            args = [device, value]

        # invoke callback function with device and value (if applicable) as parameters
        thread = threading.Thread(target=callback, args=args, daemon=True)
        thread.start()

    def access_osc_ch_property(self, callback, value=None):
        """
        Invokes the specified function with the currently selected oscilloscope & its selected channel as well as
        the given value as parameters.

        This method is used to apply any desired setting to the currently selected oscilloscope channel.
        However, the actual function call and the ensuing setting to the channel is delegated to a separate thread.

        Args:
            callback (function):
                The function to call in a separate thread.
            value (str):
                The (optional) third parameter to pass to the callback function.
        """
        self._mutex_osc_ch_selection.acquire()
        channel = self.selected_osc_ch
        self._mutex_osc_ch_selection.release()

        self._mutex_osc_selection.acquire()
        device = self.selected_osc
        self._mutex_osc_selection.release()

        # convert QML's NaN (or empty String) into Python's None if necessary, forward the parameter otherwise
        if value is None:
            args = [device, channel]
        elif value == 'NaN' or value == '':
            args = [device, channel, None]
        else:
            args = [device, channel, value]

        # invoke callback function with device, channel and value (if applicable) as parameters
        thread = threading.Thread(target=callback, args=args, daemon=True)
        thread.start()

    def access_gen_property(self, callback, value=None):
        """
        Invokes the specified function with the currently selected generator and the given value as parameters.

        This method is used to apply any desired setting to the currently selected generator.
        However, the actual function call and the ensuing setting to the device is delegated to a separate thread.

        Args:
            callback (function):
                The function to call in a separate thread.
            value (str):
                The (optional) second parameter to pass to the callback function.
        """
        self._mutex_gen_selection.acquire()
        device = self.selected_gen
        self._mutex_gen_selection.release()

        # convert QML's NaN (or empty String) into Python's None if necessary, forward the parameter otherwise
        if value is None:
            args = [device]
        elif value == 'NaN' or value == '':
            args = [device, None]
        else:
            args = [device, value]

        # invoke callback function with device and value (if applicable) as parameters
        thread = threading.Thread(target=callback, args=args, daemon=True)
        thread.start()

    def access_gen_ch_property(self, callback, value=None):
        """
        Invokes the specified function with the currently selected generator & its selected channel as well as
        the given value as parameters.

        This method is used to apply any desired setting to the currently selected generator channel.
        However, the actual function call and the ensuing setting to the channel is delegated to a separate thread.

        Args:
            callback (function):
                The function to call in a separate thread.
            value (str):
                The (optional) third parameter to pass to the callback function.
        """
        self._mutex_gen_ch_selection.acquire()
        channel = self.selected_gen_ch
        self._mutex_gen_ch_selection.release()

        self._mutex_gen_selection.acquire()
        device = self.selected_gen
        self._mutex_gen_selection.release()

        # convert QML's NaN (or empty String) into Python's None if necessary, forward the parameter otherwise
        if value is None:
            args = [device, channel]
        elif value == 'NaN' or value == '':
            args = [device, channel, None]
        else:
            args = [device, channel, value]

        # invoke callback function with device, channel and value (if applicable) as parameters
        thread = threading.Thread(target=callback, args=args, daemon=True)
        thread.start()
