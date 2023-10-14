import handyscope
from PySide6.QtCore import QPointF

import hantekosc
from uniswag.devices.oscilloscope import Oscilloscope, OscChannel


class HantekOsc(Oscilloscope):
    def __init__(self, name, ser_no, was_stopped_callback):
        """
        A Hantek oscilloscope interface, inherits from Oscilloscope.

        The interface connects to and communicates with an oscilloscope object from the "hantekosc" library.
        This "hantekosc" oscilloscope object is stored in a private attribute.

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

        Returns:
            HantekOsc:
                A HantekOsc object.
        """
        super().__init__('Hantek', name, ser_no, was_stopped_callback)

        # create the library-specific oscilloscope object which to interface with
        self._osc = hantekosc.Oscilloscope(serial_number=ser_no)

        # fill the oscilloscope's channel list
        i = 0
        for channel_obj in self._osc.channels:
            self._ch.append(HantekOscChannel('Channel', i + 1, self._mutex_dev_access, channel_obj))
            i += 1

        # Fetch the data from the device after the device is already stopped again
        self._data_not_fetched_from_last_run = False

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
                min_voltage = None
                max_voltage = None

                frequency = [0]
                min_share = None
                max_share = None

                # get the time vector from the oscilloscope
                self._mutex_dev_access.acquire()
                time = self._osc.channels[0].retrieved_data[0]
                self._mutex_dev_access.release()

                raw_data = None

                # convert the raw measurement data into QPoint arrays for each enabled channel
                # and save both the minimum & maximum value
                for i in range(self.ch_cnt):

                    self._mutex_dev_access.acquire()
                    # retrieve the raw measurement data from the oscilloscope only if the channel is enabled
                    if self._ch[i].is_enabled and self._ch[i].new_data_ready:
                        raw_data = self._osc.channels[i].retrieved_data[1]

                        self._mutex_dev_access.release()

                        # combine each element from the time vector and one channel's raw measurement data
                        # into a QPoint
                        current_norm_points = [QPointF(time[j], raw_data[j]) for j in range(
                            min(len(time), len(raw_data)))]

                        # calculate FFT
                        frequency, share = self.calculate_fft_points(time, raw_data)
                        current_fft_points = [QPointF(frequency[j], share[j]) for j in range(len(frequency))]

                        # use the channel's number as key and the QPoint array tuple as value
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
                        self._mutex_dev_access.release()

                self._mutex_running.release()

                # skip value updates if not a single channel was enabled
                if raw_data is not None:
                    lim_norm = {'Time': (time[0], time[-1]), 'Voltage': (min_voltage, max_voltage)}
                    lim_fft = {'Frequency': (frequency[0], frequency[-1]), 'Share': (min_share, max_share)}

                    self._mutex_data.acquire()

                    # update the dictionaries containing
                    # the latest measured data points and the minimum & maximum values
                    self._points = points
                    self._limits_norm = lim_norm
                    self._limits_fft = lim_fft

                    # indicate that new values have been retrieved from the oscilloscope
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
        result = self._osc.running
        self._mutex_dev_access.release()

        return result

    def start(self):
        success = False
        all_channels_disabled = True

        # assert that the oscilloscope is not currently mid-measurement
        self._mutex_running.acquire()

        self._mutex_dev_access.acquire()

        # only start the measurement if it has not already been started
        if not self._osc.running:

            # ensure that at least one channel is enabled before starting the measurement
            for ch in self._ch:
                if ch.is_enabled:
                    all_channels_disabled = False
                    break
            if not all_channels_disabled:
                self._osc.start()
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
        if self._osc.running:
            self._osc.stop()
            success = True

        self._mutex_dev_access.release()
        self._mutex_running.release()

        return success


    @property
    def sample_freq_max(self):
        self._mutex_dev_access.acquire()
        result = self._osc.max_sample_rate
        self._mutex_dev_access.release()

        return result

    @property
    def sample_freq(self):
        self._mutex_dev_access.acquire()
        result = self._osc.sample_rate
        self._mutex_dev_access.release()

        return result

    @sample_freq.setter
    def sample_freq(self, value):
        # assert that minimum value is 1
        value = max(value, 1)

        self._mutex_dev_access.acquire()

        # assert that maximum value is not exceeded
        self._osc.sample_rate = min(value, self._osc.max_sample_rate)

        self._mutex_dev_access.release()

    @property
    def rec_len_max(self):
        self._mutex_dev_access.acquire()
        result = self._osc.max_record_length
        self._mutex_dev_access.release()

        return result

    @property
    def rec_len(self):
        self._mutex_dev_access.acquire()
        result = self._osc.record_length
        self._mutex_dev_access.release()

        return result

    @rec_len.setter
    def rec_len(self, value):
        # assert that minimum value is 1
        value = max(value, 1)

        self._mutex_dev_access.acquire()
        # assert that maximum value is not exceeded
        self._osc.record_length = min(value, self._osc.max_record_length)
        self._mutex_dev_access.release()

    @property
    def pre_sample_ratio(self):
        self._mutex_dev_access.acquire()
        result = self._osc.pre_sample_ratio
        self._mutex_dev_access.release()

        return result

    @pre_sample_ratio.setter
    def pre_sample_ratio(self, value):
        # assert that value is within the minimum-maximum-range
        value = min(1, max(0, value))

        self._mutex_dev_access.acquire()
        self._osc.pre_sample_ratio = value
        self._mutex_dev_access.release()


class HantekOscChannel(OscChannel):
    def __init__(self, name, ch_no, mutex, ch):
        """
        A Hantek  channel interface, inherits from OscChannel.

        The interface connects to and communicates with an oscilloscope channel object from the "hantekosc" library.
        This "hantekosc" oscilloscope channel object is stored in a private attribute.

        Args:
            name (str):
                The moniker of the oscilloscope channel.
                Used for the 'Name' part of the channel's ID.
            ch_no (int):
                The number of the oscilloscope channel.
                Used for the 'No' part of the channel's ID.
            mutex (threading.Lock):
                The same threading lock that is used for every other property access to the associated device.
            ch (hantekosc.Channel):
                The library-specific channel object which to interface with.

        Returns:
            HantekOscChannel:
                A HantekOscChannel object.
        """
        super().__init__(name, ch_no, mutex)

        # save the library-specific channel object
        self._ch = ch

        # disable the channel initially
        self._ch.is_enabled = False

    @OscChannel.is_enabled.setter
    def is_enabled(self, value):
        self._mutex_dev_access.acquire()
        self._is_enabled = value
        self._mutex_dev_access.release()

    @property
    def ranges_avail(self):
        self._mutex_dev_access.acquire()
        result =self._ch.voltage_ranges_available
        self._mutex_dev_access.release()

        return result

    @property
    def range(self):
        self._mutex_dev_access.acquire()
        result = self._ch.voltage_range
        self._mutex_dev_access.release()

        return result

    @range.setter
    def range(self, value):
        self._mutex_dev_access.acquire()
        self._ch.voltage_range = value
        self._mutex_dev_access.release()

    @property
    def trig_kinds_avail(self):
        self._mutex_dev_access.acquire()
        result = self._ch.trigger_kinds_available
        self._mutex_dev_access.release()

        return result

    @property
    def trig_kind(self):
        self._mutex_dev_access.acquire()
        result = self._ch.trigger_kind
        self._mutex_dev_access.release()

        return result

    @trig_kind.setter
    def trig_kind(self, value):
        self._mutex_dev_access.acquire()
        self._ch.trigger_kind = value
        self._mutex_dev_access.release()

    @property
    def trig_lvl(self):
        self._mutex_dev_access.acquire()
        result = [self._ch.trigger_level]
        self._mutex_dev_access.release()

        return result

    @trig_lvl.setter
    def trig_lvl(self, value):
        self._mutex_dev_access.acquire()
        self._ch.trigger_level = value[0]
        self._mutex_dev_access.release()

    @property
    def new_data_ready(self):
        data = self._ch.new_data_ready
        return data
