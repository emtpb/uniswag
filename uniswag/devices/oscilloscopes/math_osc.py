import numpy as np
from PySide6.QtCore import QPointF

from uniswag.devices.oscilloscope import Oscilloscope, OscChannel


class MathOsc(Oscilloscope):
    def __init__(self, name, ser_no, was_stopped_callback, device_manager):
        """
        A simulated oscilloscope, inherits from Oscilloscope.

        Allows for various mathematical operations using other oscilloscopes' channels as operands.

        Args:
            name (str):
                The moniker of the oscilloscope.
                Used for the 'Name' part of the device's ID.
            ser_no (str):
                The serial number of the oscilloscope.
                Used for the 'SerNo' part of the device's ID.
            was_stopped_callback (function):
                A callback function which will be invoked when the device's measurement was stopped.
                Receives the device's ID as parameter.
            device_manager (uniswag.device_manager.DeviceManager):
                A device manager that provides a list of connected oscilloscopes
                so that the retrieved measurement data can be used for calculations.

        Returns:
            MathOsc:
                A MathOsc object.
        """
        super().__init__('MS-SWAG', name, ser_no, was_stopped_callback)

        # the device manager provides access to the device list, and consequentially, the list of oscilloscopes
        self._device_manager = device_manager

        # fill the oscilloscope's channel list
        self._ch.append(MathOscChannel('Channel', 1, self._mutex_dev_access, self._id, self._device_manager))

        # halt the oscilloscope's measurement initially
        self._is_running = False

        # start the thread that continuously retrieves new measurement data while the oscilloscope is running
        self._new_data_retrieval_thread.start()

    def _retrieve_new_data(self):
        while True:
            # limit loop execution speed by waiting inbetween iterations
            self._data_retrieval_speed_limiter.acquire(timeout=0.001)

            # assert that the oscilloscope is not stopped mid-measurement
            self._mutex_running.acquire()

            # retrieve new measurement data from the oscilloscope if it is currently running
            if self.is_running:
                points = {}
                min_voltage = max_voltage = None

                frequency = [0]
                min_share = max_share = None

                time = None

                # convert the raw measurement data into QPoint arrays for each enabled channel
                # and save both the minimum & maximum value
                for i in range(self.ch_cnt):

                    self._mutex_dev_access.acquire()

                    # retrieve the time vector and measurement data only if the channel is enabled
                    if self._ch[i].is_enabled:
                        valid, time, raw_data = self._ch[i].retrieve()

                        self._mutex_dev_access.release()

                        if valid:
                            # combine each element from the time vector and one channel's raw measurement data
                            # into a QPoint
                            current_norm_points = [QPointF(time[j], raw_data[j]) for j in range(len(time))]

                            # calculate FFT
                            frequency, share = self.calculate_fft_points(time, raw_data)
                            current_fft_points = [QPointF(frequency[j], share[j]) for j in range(len(frequency))]

                            # use the channel's number as the key and the QPoint array tuple as the value
                            points[i + 1] = (current_norm_points, current_fft_points)

                            # set minimum and maximum across all channels
                            if min_voltage is None and max_voltage is None:
                                min_voltage = min(raw_data)
                                max_voltage = max(raw_data)
                            else:
                                min_voltage = min(min_voltage, min(raw_data))
                                max_voltage = max(max_voltage, max(raw_data))
                            if min_share is None and max_share is None:
                                min_share = min(share)
                                max_share = max(share)
                            else:
                                min_share = min(min_share, min(share))
                                max_share = max(max_share, max(share))
                        else:
                            time = None

                    else:
                        self._mutex_dev_access.release()

                self._mutex_running.release()

                # skip value updates if not a single channel was enabled
                if time is not None:
                    lim_norm = {'Time': (time[0], time[-1]), 'Voltage': (min_voltage, max_voltage)}
                    lim_fft = {'Frequency': (frequency[0], frequency[-1]), 'Share': (min_share, max_share)}

                    self._mutex_data.acquire()

                    # update the dictionaries containing
                    # the latest measured data points and the minimum & maximum values
                    self._points = points
                    self._limits_norm = lim_norm
                    self._limits_fft = lim_fft

                    # indicate that new values have been retrieved
                    self._new_data_available = True

                    self._mutex_data.release()

            else:
                self._mutex_running.release()

                # invoke the callback function to signal that the oscilloscope was stopped
                self._was_stopped(self._id)

                # halt the measurement while the oscilloscope is stopped
                with self._cond_running:
                    self._cond_running.wait()

    def _term_deletion(self):
        pass

    @property
    def is_running(self):
        self._mutex_dev_access.acquire()
        result = self._is_running
        self._mutex_dev_access.release()

        return result

    def start(self):
        success = False
        all_channels_disabled = True

        # assert that the oscilloscope is not currently mid-measurement
        self._mutex_running.acquire()

        self._mutex_dev_access.acquire()

        # only start the measurement if it has not already been started
        if not self._is_running:

            # ensure that at least one channel is enabled before starting the measurement
            for ch in self._ch:
                if ch.is_enabled:
                    all_channels_disabled = False
                    break
            if not all_channels_disabled:
                self._is_running = True
                success = True

        self._mutex_dev_access.release()
        self._mutex_running.release()

        if success:

            # resume the thread dedicated to the retrieval of new data
            with self._cond_running:
                self._cond_running.notifyAll()

        return success

    def stop(self):
        success = False

        # assert that the oscilloscope is not currently mid-measurement
        self._mutex_running.acquire()

        self._mutex_dev_access.acquire()

        # only stop the measurement if it has not already been stopped
        if self._is_running:
            self._is_running = False
            success = True

        self._mutex_dev_access.release()
        self._mutex_running.release()

        return success

    def add_ch(self):
        """
        Adds one channel to the oscilloscope's channel list.

        Returns:
            dict[str, Any]:
                The ID of the added channel.
        """
        self._mutex_dev_access.acquire()
        added_channel = MathOscChannel(
            'Channel', self.ch_cnt + 1, self._mutex_dev_access, self._id, self._device_manager)
        self._ch.append(added_channel)
        self._mutex_dev_access.release()

        return added_channel.id

    def remove_ch(self):
        """
        Removes the channel from the oscilloscope's channel list which was added last.

        The minimum valid channel count is 1,
        so no changes to the channel list will take place if this method is called when there is only one entry left.
        The same will happen when attempting to invoke this method while the oscilloscope not stopped.

        Returns:
            dict[str, Any] or None:
                The ID of the removed channel on removal success,
                None otherwise (if the channel count is already at minimum OR the oscilloscope is currently running).
        """
        removed_channel = None

        self._mutex_dev_access.acquire()

        if not self._is_running:

            # keep at least one channel
            if self.ch_cnt > 1:
                removed_channel = self._ch.pop()
                for func in removed_channel.deletion_callbacks():
                    func()

        self._mutex_dev_access.release()

        if removed_channel is not None:
            return removed_channel.id
        else:
            return removed_channel


# noinspection PyUnresolvedReferences
# noinspection PyTypedDict
class MathOscChannel(OscChannel):
    def __init__(self, name, ch_no, mutex, osc_id, devices):
        """
        A simulated channel, inherits from OscChannel.

        Stores two channel objects from other oscilloscopes in order to retrieve their measurement data
        and calculate a specified mathematical function using the retrieved voltage values.
        These two channel objects are referred to as "operands",
        while the mathematical function is referred to as the "operator".

        Args:
            name (str):
                The moniker of the oscilloscope channel.
                Used for the 'Name' part of the channel's ID.
            ch_no (int):
                The number of the oscilloscope channel.
                Used for the 'No' part of the channel's ID.
            mutex (threading.Lock):
                The same threading lock that is used for every other property access to the associated device.
            osc_id (dict[str, str]):
                The ID of the oscilloscope to which this channel belongs.
                Used for internal comparisons to prevent infinite recursion
                by setting one of the channel's operands to the channel itself.
            devices (uniswag.device_manager.DeviceManager):
                A device manager that provides a list of connected oscilloscopes.
                This list will be used for the selection of available mathematical operands.

        Returns:
            MathOscChannel:
                A MathOscChannel object.
        """
        super().__init__(name, ch_no, mutex)

        # the ID of the MathOsc to which this channel belongs to
        self._osc_id = osc_id

        # provides the device list, and therefore, the list of oscilloscopes
        self._devices = devices

        # both mathematical operands are each defined by an oscilloscope and one of its channels;
        # the mathematical operation will be executed using the values retrieved from these two channels
        self._operand1 = {'Device': None, 'Channel': None}
        self._operand2 = {'Device': None, 'Channel': None}

        # added to the time vector values of the second operand, effectively moving the graph along the X axis
        self._shift = 0

        # the method receiving both operands' voltage value vectors as parameters
        self._operator = self._add

        # a dictionary mapping every available mathematical operator to a corresponding method
        self._operators_avail = {
            '+': self._add,
            '-': self._subtract,
            '*': self._multiply,
            '<- min ->': self._min,
            '<- max ->': self._max
        }

    @OscChannel.is_enabled.setter
    def is_enabled(self, value):
        self._mutex_dev_access.acquire()
        self._is_enabled = value
        self._mutex_dev_access.release()

    def retrieve(self):
        """
        Retrieves the current measurement data from both of the operands
        and performs the calculation determined by the operator on that data.

        Each operand's measurement data is interpolated in order to achieve a common time vector.
        Afterwards, both data sets are passed to the operator function and the results are returned.

        Returns:
            (bool, np.ndarray, np.ndarray):
                A tuple with the first value indicating, whether the other two values are valid
                (False if no data could be retrieved).
                The second value represents the time vector.
                The third value is the resulting voltage vector (after applying the operator).
        """
        if self._operand1['Channel'] is None or self._operand2['Channel'] is None:
            return False, [], []

        try:
            graph1 = self._operand1['Device'].retrieve()['Points'][self._operand1['Channel'].id['No']][0]
            graph2 = self._operand2['Device'].retrieve()['Points'][self._operand2['Channel'].id['No']][0]
        except KeyError:
            return False, [], []

        x_vec1 = []
        y_vec1 = []
        x_vec2 = []
        y_vec2 = []

        for point in graph1:
            x_vec1.append(point.x())
            y_vec1.append(point.y())
        for point in graph2:
            x_vec2.append(point.x() + self._shift)
            y_vec2.append(point.y())

        time = np.unique(np.concatenate((x_vec1, x_vec2)))

        op1 = np.interp(time, x_vec1, y_vec1, left=0, right=0)
        op2 = np.interp(time, x_vec2, y_vec2, left=0, right=0)

        voltage = self._operator(op1, op2)

        return True, time, voltage

    @property
    def operands_avail(self):
        """
        The available operands.

        Valid operands are any channels from any oscilloscope except *this* MathOscChannel object itself.

        Returns:
             dict[str, (uniswag.devices.device.Device, uniswag.devices.device.Channel) or (None, None)]:
                A dictionary that maps a tuple of Oscilloscope & Channel objects to the respective ID combination.
        """
        result = {}

        for dev in self._devices.device_list:
            if dev.id['DevType'] == 'Osc':
                for c in dev.ch:
                    if dev.id != self._osc_id or (dev.id == self._osc_id and c.id != self._id):
                        operand_id = dev.id['Vendor'] + ' ' + dev.id['Name'] + ' (' + dev.id['SerNo'] + ') - '\
                            + c.id['Name'] + ' ' + str(c.id['No'])
                        result[operand_id] = (dev, c)

        result['-'] = (None, None)

        return result

    @property
    def operand1(self):
        """
        The first of two operands monitored by this channel.

        Returns:
             str:
                The first operand represented by the combination of its oscilloscope's & channel's IDs.
        """
        if self._operand1['Channel'] is None:
            return '-'

        self._mutex_dev_access.acquire()
        dev_id = self._operand1['Device'].id
        ch_id = self._operand1['Channel'].id
        self._mutex_dev_access.release()

        result = dev_id['Vendor'] + ' ' + dev_id['Name'] + ' (' + dev_id['SerNo'] + ') - '\
            + ch_id['Name'] + ' ' + str(ch_id['No'])

        return result

    @operand1.setter
    def operand1(self, value):
        """
        Sets the first of two operands monitored by this channel.

        Args:
             value (str):
                The new operand represented by the combination of its oscilloscope's & channel's IDs.
        """
        operand = self.operands_avail[value]
        self._mutex_dev_access.acquire()

        if self._operand1['Channel'] is not None:
            self._operand1['Channel'].set_deletion_callback(self._osc_id, self._id)

        self._operand1['Device'] = operand[0]
        self._operand1['Channel'] = operand[1]

        if self._operand1['Channel'] is not None:
            self._operand1['Channel'].set_deletion_callback(self._osc_id, self._id, self._operand1_reset)

        self._mutex_dev_access.release()

    def _operand1_reset(self):
        """
        Clears the first of two operands monitored by this channel.
        """
        self._operand1['Device'] = None
        self._operand1['Channel'] = None

    @property
    def operand2(self):
        """
        The second of two operands monitored by this channel.

        Returns:
             str:
                The second operand represented by the combination of its oscilloscope's & channel's IDs.
        """
        if self._operand2['Channel'] is None:
            return '-'

        self._mutex_dev_access.acquire()
        dev_id = self._operand2['Device'].id
        ch_id = self._operand2['Channel'].id
        self._mutex_dev_access.release()

        result = dev_id['Vendor'] + ' ' + dev_id['Name'] + ' (' + dev_id['SerNo'] + ') - ' \
            + ch_id['Name'] + ' ' + str(ch_id['No'])

        return result

    @operand2.setter
    def operand2(self, value):
        """
        Sets the second of two operands monitored by this channel.

        Args:
             value (str):
                The new operand represented by the combination of its oscilloscope's & channel's IDs.
        """
        operand = self.operands_avail[value]
        self._mutex_dev_access.acquire()

        if self._operand2['Channel'] is not None:
            self._operand2['Channel'].set_deletion_callback(self._osc_id, self._id)

        self._operand2['Device'] = operand[0]
        self._operand2['Channel'] = operand[1]

        if self._operand2['Channel'] is not None:
            self._operand2['Channel'].set_deletion_callback(self._osc_id, self._id, self._operand2_reset)

        self._mutex_dev_access.release()

    def _operand2_reset(self):
        """
        Clears the second of two operands monitored by this channel.
        """
        self._operand2['Device'] = None
        self._operand2['Channel'] = None

    @property
    def shift(self):
        """
        The displacement of the second operand's graph along the X-axis in seconds.

        This value is added to each element of the operand's time vector,
        which effectively shifts it by the set amount of seconds.
        """
        self._mutex_dev_access.acquire()
        result = self._shift
        self._mutex_dev_access.release()

        return result

    @shift.setter
    def shift(self, value):
        """
        Sets the displacement of the second operand's graph along the X-axis in seconds.

        This value is added to each element of the operand's time vector,
        which effectively shifts it by the set amount of seconds.
        """
        self._mutex_dev_access.acquire()
        self._shift = value
        self._mutex_dev_access.release()

    @property
    def operators_avail(self):
        """
        The collection of mathematical functions which can be performed on the two set operands.

        Returns:
             list[str]:
                The available operators represented by their mathematical symbols.
        """
        return list(self._operators_avail.keys())

    @property
    def operator(self):
        """
        The mathematical function that is currently performed on the two set operands.

        Returns:
             str:
                The currently set operator represented by its mathematical symbol.
        """
        self._mutex_dev_access.acquire()
        current_operator = self._operator
        self._mutex_dev_access.release()

        for result, func in self._operators_avail.items():
            if func == current_operator:
                return result

    @operator.setter
    def operator(self, value):
        """
        Sets the mathematical function that is performed on the two set operands.

        Args:
             value (str):
                The new operator represented by its mathematical symbol.
        """
        self._mutex_dev_access.acquire()
        self._operator = self._operators_avail[value]
        self._mutex_dev_access.release()

    @staticmethod
    def _add(op1, op2):
        """
        Adds up both operands.

        Args:
            op1 (np.ndarray):
                The first operand's voltage vector.
            op2 (np.ndarray):
                The second operand's voltage vector.

        Returns:
             np.ndarray:
                The new vector containing the result of the element-wise summation of the two specified vectors.
        """
        return np.add(op1, op2)

    @staticmethod
    def _subtract(op1, op2):
        """
        Subtracts the second operand from the first one.

        Args:
            op1 (np.ndarray):
                The first operand's voltage vector.
            op2 (np.ndarray):
                The second operand's voltage vector.

        Returns:
             np.ndarray:
                The new vector containing the result of the element-wise subtraction of the two specified vectors.
        """
        return np.subtract(op1, op2)

    @staticmethod
    def _multiply(op1, op2):
        """
        Multiplies both operands.

        Args:
            op1 (np.ndarray):
                The first operand's voltage vector.
            op2 (np.ndarray):
                The second operand's voltage vector.

        Returns:
             np.ndarray:
                The new vector containing the result of the element-wise multiplication of the two specified vectors.
        """
        return np.multiply(op1, op2)

    @staticmethod
    def _min(op1, op2):
        """
        Provides the minimum values across both operands.

        Args:
            op1 (np.ndarray):
                The first operand's voltage vector.
            op2 (np.ndarray):
                The second operand's voltage vector.

        Returns:
             np.ndarray:
                The new vector containing the minima of the element-wise comparison of the two specified vectors.
        """
        return np.minimum(op1, op2)

    @staticmethod
    def _max(op1, op2):
        """
        Provides the maximum values across both operands.

        Args:
            op1 (np.ndarray):
                The first operand's voltage vector.
            op2 (np.ndarray):
                The second operand's voltage vector.

        Returns:
             np.ndarray:
                The new vector containing the maxima of the element-wise comparison of the two specified vectors.
        """
        return np.maximum(op1, op2)
