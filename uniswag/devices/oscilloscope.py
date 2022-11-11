import threading

import numpy as np
import scipy.fft as fft
from PySide6.QtCore import QPointF

from uniswag.devices.device import Device, Channel


class Oscilloscope(Device):
    def __init__(self, vendor, name, ser_no, was_stopped_callback):
        """
        Base class for all oscilloscopes, inherits from Device.

        Possesses a method to retrieve the latest measurement data,
        which is continuously updated by a thread in the background.
        Whenever the thread halts (due to the measurement not running anymore),
        the given callback function is invoked with the device's ID as parameter.

        Args:
            vendor (str):
                The name of the oscilloscope's vendor.
                Used for the 'Vendor' part of the device's ID.
            name (str):
                The moniker of the oscilloscope.
                Used for the 'Name' part of the device's ID.
            ser_no (str):
                The serial number of the oscilloscope.
                Used for the 'SerNo' part of the device's ID.
            was_stopped_callback (function):
                The callback function to invoke when the device's measurement was stopped.

        Returns:
            Oscilloscope:
                An Oscilloscope object.
        """
        super().__init__(vendor, name, ser_no, 'Osc')

        # a threading lock which ensures thread-safe access to
        # the latest measured data points (= voltage and time samples)
        self._mutex_data = threading.Lock()

        # a threading lock which ensures that the oscilloscope cannot be stopped mid-measurement
        self._mutex_running = threading.Lock()

        # a threading lock which limits the execution speed of the data retrieval thread
        self._data_retrieval_speed_limiter = threading.Lock()
        self._data_retrieval_speed_limiter.acquire()

        # a threading condition which halts the data retrieval thread while the oscilloscope is stopped
        self._cond_running = threading.Condition()

        # the dictionary containing the latest measured data points;
        # each key represents a channel, to which the corresponding two lists of data points belongs
        # (first list for directly measured data, second list for fourier-transformed data)
        self._points = {1: ([QPointF(0, 0)], [QPointF(0, 0)])}

        # the minimum and maximum measurement values in the entire data points dictionary
        self._limits_norm = {'Time': (0, 0), 'Voltage': (0, 0)}
        # the minimum and maximum FFT values in the entire data points dictionary
        self._limits_fft = {'Frequency': (0, 0), 'Share': (0, 0)}

        # indicates, whether the data points dictionary has been updated since the last time it was read
        self._new_data_available = False

        # a thread that continuously retrieves new measurement data while the oscilloscope is running
        self._new_data_retrieval_thread = threading.Thread(target=self._retrieve_new_data, daemon=True)

        # a callback function that is invoked when the thread dedicated to the retrieval of new data is halted
        # (manually or autonomously)
        self._was_stopped = was_stopped_callback

    def init_deletion(self):
        for c in self._ch:
            for func in c.deletion_callbacks():
                func()
        self._term_deletion()

    def retrieve(self, dismiss=False):
        """
        Provides the latest measurement data of all enabled channels.

        Along with the measured data points,
        the range limits (= minimum & maximum values from the data points) are supplied,
        as well as an indicator for whether all these values have changed since the last method call.

        Args:
            dismiss (bool):
                If set to True, the flag which labels the retrieved data as "new" is cleared.
                Otherwise, it remains as is, even if the same values have already been retrieved in a previous call.

        Returns:
            dict[str, Any]:
                A dictionary with the following four keys:
                'New' is a flag which indicates that there might be unread values (True if new).
                'Points' contains a dictionary with the enabled channels' numbers as keys and
                the measured data points in the form of two lists (normal and FFT) combined into a tuple as values.
                'Norm limits' contains a dictionary with 'Time' and 'Voltage' as keys and
                tuples of the respective minimum and maximum as values.
                'FFT limits' is the same but with 'Frequency' and 'Share' keys.
        """
        new_data = False

        self._mutex_data.acquire()

        # check if the measured data points and limits have been updated by
        # the thread dedicated to the retrieval of new data (since the last method call)
        if self._new_data_available:
            if dismiss:
                self._new_data_available = False
            new_data = True

        # get the latest data points and limits
        points = self._points
        lim_norm = self._limits_norm
        lim_fft = self._limits_fft

        self._mutex_data.release()

        return {
            'New': new_data,
            'Points': points,
            'Norm limits': lim_norm, 'FFT limits': lim_fft
        }

    @staticmethod
    def calculate_fft_points(x_points, y_points):
        """
        Performs a Fast Fourier Transform on the specified time signal.

        Args:
            x_points (list):
                The original signal's time vector.
            y_points (list):
                The original signal's voltage vector.

        Returns:
            (np.ndarray, np.ndarray):
                A tuple containing the resulting frequency- & share-vector.
        """
        sample_points = len(x_points)
        sample_spacing = max(x_points) / len(x_points)

        yf = 2.0 / sample_points * np.abs(fft.fft(y_points)[0:sample_points // 2])
        xf = fft.fftfreq(sample_points, sample_spacing)[:sample_points // 2]
        return xf, yf

    # ABSTRACT METHODS #################################################################################################

    def _retrieve_new_data(self):
        """
        Continuously retrieves new measurement data for each enabled channel while the oscilloscope is running.

        Accordingly, the dictionaries containing the latest data points and value limits,
        which are read out by the retrieving method, are updated with the new values.
        Furthermore, the boolean value indicating that new data exists is set to True.
        """
        raise NotImplementedError

    def _term_deletion(self):
        """
        Performs library-specific actions in order to cleanly disconnect certain vendor's devices.

        When the device's "pseudo-destructor" is called, it will invoke this method as a final step.
        """
        raise NotImplementedError

    @property
    def is_running(self):
        raise NotImplementedError

    def start(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError


class OscChannel(Channel):
    def __init__(self, name, ch_no, mutex):
        """
        Base class for all oscilloscope channels, inherits from Channel.

        Args:
            name (str):
                The moniker of the oscilloscope channel.
                Used for the 'Name' part of the channel's ID.
            ch_no (int):
                The number of the oscilloscope channel.
                Used for the 'No' part of the channel's ID.
            mutex (threading.Lock):
                The same threading lock that is used for every other property access to the associated device.

        Returns:
            OscChannel:
                An OscChannel object.
        """
        super().__init__(name, ch_no, mutex)

        # a dictionary that allows to invoke multiple callback functions from different Channel objects
        # upon calling the "pseudo-destructor" method of the Oscilloscope object to which this Channel object belongs to
        # by mapping each function to a tuple of oscilloscope & channel ID
        self._was_removed = {}

    def deletion_callbacks(self):
        """
        The list of callback functions invoked upon
        calling the superordinate Oscilloscope object's "pseudo-destructor" method.

        Therefore, every callback in this list is executed
        once the oscilloscope is removed from the device list.
        No parameters are passed to the callbacks.

        Returns:
            list[function]:
                The callback functions to invoke in the superordinate Oscilloscope object's "pseudo-destructor".
        """
        return list(self._was_removed.values())

    def set_deletion_callback(self, osc_id, ch_id, func=None):
        """
        Adds/removes a function to/from the dictionary of callbacks
        which all are invoked upon calling the superordinate Oscilloscope object's "pseudo-destructor" method.

        Therefore, every callback added via this method will be executed
        once the oscilloscope is removed from the device list.
        No parameters are passed to the callbacks.

        Args:
            osc_id (dict[str, str]):
                The ID of the oscilloscope to which the channel belongs to.
            ch_id (dict[str, Any]):
                The ID of the channel to which the callback function belongs to.
            func (function):
                The function to add to the dictionary of callbacks.
                To remove an existing callback from the dictionary, this parameter needs to be omitted.
        """
        osc = frozenset(osc_id.values())
        ch = frozenset(ch_id.values())

        if func is not None:
            self._was_removed[(osc, ch)] = func
        else:
            self._was_removed.pop((osc, ch), None)

    # ABSTRACT METHODS #################################################################################################

    @Channel.is_enabled.setter
    def is_enabled(self, value):
        raise NotImplementedError
