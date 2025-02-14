import tektronixosc
from PySide6.QtCore import QPointF

from uniswag.devices.oscilloscope import Oscilloscope, OscChannel


class TektronixOsc(Oscilloscope):

    TRIGGER_MODES = {
        'Edge': 'edge',
        'Pulse': 'pulse'
    }

    TRIGGER_SLOPES = {
        'Rising edge': 'rising',
        'Falling edge': 'falling'
    }

    TRIGGER_SOURCES = {
        'Channel 1': 'ch1',
        'Channel 2': 'ch2',
        'Line': 'line',
        'Aux': 'aux'
    }

    def __init__(self, name, ser_no, was_stopped_callback):
        """
        A Tektronix TBS1000C interface, inherits from Oscilloscope.

        The interface connects to and communicates with an oscilloscope object from the "tektronixosc" library.
        This "tektronixosc" oscilloscope object is stored in a private attribute.

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
            TektronixOsc:
                A TektronixOsc object.
        """
        super().__init__('Tektronix', name, ser_no, was_stopped_callback)

        # create the library-specific oscilloscope object which to interface with
        self._osc = tektronixosc.Oscilloscope(resource=ser_no)

        # fill the oscilloscope's channel list
        i = 0
        for channel_obj in self._osc.channels:
            self._ch.append(TektronixOscChannel('Channel', i + 1, self._mutex_dev_access, channel_obj))
            i += 1

        # halt the oscilloscope's measurement initially
        self._is_running = False

        self._osc.data_source = 'ch1'

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
                time = []

                raw_data = None

                # convert the raw measurement data into QPoint arrays for each enabled channel
                # and save both the minimum & maximum value
                for i in range(self.ch_cnt):

                    self._mutex_dev_access.acquire()

                    # retrieve the raw measurement data from the oscilloscope only if the channel is enabled
                    if self._ch[i].is_enabled:
                        time, raw_data = self._osc.channels[i].get_signal()

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
                self._osc.run()
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
            self._osc.stop()
            success = True

        self._mutex_dev_access.release()
        self._mutex_running.release()

        return success

    def reset(self):
        self._osc.reset()

    @property
    def rec_len_max(self):
        return 20000

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
        self._osc.record_length = min(value, self.rec_len_max)

        self._mutex_dev_access.release()

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

    @property
    def trig_modes_avail(self):
        return list(self.TRIGGER_MODES.keys())

    @property
    def trig_mode(self):
        self._mutex_dev_access.acquire()
        trig_modes = dict([(value, key) for key, value in self.TRIGGER_MODES.items()])
        result = trig_modes[self._osc.trig_type]
        self._mutex_dev_access.release()

        return result

    @trig_mode.setter
    def trig_mode(self, value):
        self._mutex_dev_access.acquire()
        self._osc.trig_type = self.TRIGGER_MODES[value]
        self._mutex_dev_access.release()

    @property
    def trig_slopes_avail(self):
        return list(self.TRIGGER_SLOPES.keys())

    @property
    def trig_slope(self):
        self._mutex_dev_access.acquire()
        trig_slopes = dict([(value, key) for key, value in self.TRIGGER_SLOPES.items()])
        result = trig_slopes[self._osc.trig_slope]
        self._mutex_dev_access.release()

        return result

    @trig_slope.setter
    def trig_slope(self, value):
        self._mutex_dev_access.acquire()
        self._osc.trig_slope = self.TRIGGER_SLOPES[value]
        self._mutex_dev_access.release()

    @property
    def trigger_sources_avail(self):
        return list(self.TRIGGER_SOURCES.keys())

    @property
    def trigger_source(self):
        self._mutex_dev_access.acquire()
        trig_sources = dict([(value, key) for key, value in self.TRIGGER_SOURCES.items()])
        result = trig_sources[self._osc.trig_source]
        self._mutex_dev_access.release()

        return result

    @trigger_source.setter
    def trigger_source(self, value):
        self._mutex_dev_access.acquire()
        self._osc.trig_source = self.TRIGGER_SOURCES[value]
        self._mutex_dev_access.release()


class TektronixOscChannel(OscChannel):

    COUPLINGS = {
        'AC': 'ac',
        'DC': 'dc'
    }

    def __init__(self, name, ch_no, mutex, ch):
        """
        A Tektronix TBS1000C channel interface, inherits from OscChannel.

        The interface connects to and communicates with an oscilloscope channel object from the "Tektronixosc" library.
        This "Tektronixosc" oscilloscope channel object is stored in a private attribute.

        Args:
            name (str):
                The moniker of the oscilloscope channel.
                Used for the 'Name' part of the channel's ID.
            ch_no (int):
                The number of the oscilloscope channel.
                Used for the 'No' part of the channel's ID.
            mutex (threading.Lock):
                The same threading lock that is used for every other property access to the associated device.
            ch (tektronixosc.oscilloscope.Channel):
                The library-specific channel object which to interface with.

        Returns:
            TektronixOscChannel:
                A TektronixOscChannel object.
        """
        super().__init__(name, ch_no, mutex)

        # save the library-specific channel object
        self._ch = ch
        self._ch.attenuation = 1

    @OscChannel.is_enabled.setter
    def is_enabled(self, value):
        self._mutex_dev_access.acquire()
        if value:
            self._ch.enabled = True
        else:
            self._ch.enabled = False
        self._is_enabled = value
        self._mutex_dev_access.release()

    @property
    def probe_offset(self):
        self._mutex_dev_access.acquire()
        result = self._ch.offset
        self._mutex_dev_access.release()

        return result

    @probe_offset.setter
    def probe_offset(self, value):
        self._mutex_dev_access.acquire()
        self._ch.offset = value
        self._mutex_dev_access.release()

    @property
    def probe_gain(self):
        self._mutex_dev_access.acquire()
        result = self._ch.attenuation
        self._mutex_dev_access.release()

        return result

    @probe_gain.setter
    def probe_gain(self, value):
        # assert that value is non-zero and within the minimum-maximum-range
        if value == 0:
            value = 1
        else:
            value = min(10000.0, max(0.1, value))

        self._mutex_dev_access.acquire()
        self._ch.attenuation = value
        self._mutex_dev_access.release()

    @property
    def couplings_avail(self):
        return list(self.COUPLINGS.keys())

    @property
    def coupling(self):
        self._mutex_dev_access.acquire()
        couplings = dict([(value, key) for key, value in self.COUPLINGS.items()])
        result = couplings[self._ch.coupling]
        self._mutex_dev_access.release()

        return result

    @coupling.setter
    def coupling(self, value):
        self._mutex_dev_access.acquire()
        self._ch.coupling = self.COUPLINGS[value]
        self._mutex_dev_access.release()

    @property
    def trig_lvl(self):
        self._mutex_dev_access.acquire()
        result = self._ch.trig_lvl
        self._mutex_dev_access.release()

        return result

    @trig_lvl.setter
    def trig_lvl(self, value):
        self._mutex_dev_access.acquire()
        self._ch.trig_lvl = value
        self._mutex_dev_access.release()
