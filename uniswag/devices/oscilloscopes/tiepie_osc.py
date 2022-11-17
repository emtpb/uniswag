import tiepie
from PySide6.QtCore import QPointF

from uniswag.devices.oscilloscope import Oscilloscope, OscChannel


class TiepieOsc(Oscilloscope):
    def __init__(self, name, ser_no, was_stopped_callback):
        """
        A TiePie engineering Handyscope interface, inherits from Oscilloscope.

        The interface connects to and communicates with an oscilloscope object from the "tiepie" library.
        This "tiepie" oscilloscope object is stored in a private attribute.

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
            TiepieOsc:
                A TiepieOsc object.
        """
        super().__init__('Tiepie', name, ser_no, was_stopped_callback)

        # create the library-specific oscilloscope object which to interface with
        self._osc = tiepie.Oscilloscope(instr_id=int(ser_no), id_kind='serial number')

        # fill the oscilloscope's channel list
        i = 0
        for channel_obj in self._osc.channels:
            self._ch.append(TiepieOscChannel('Channel', i + 1, self._mutex_dev_access, channel_obj))
            i += 1

        # set default measure mode
        self._osc.measure_mode = 'block'
        self._measure_mode = 'block'

        # define available measure modes
        self._special_measure_mode = 'repeat'
        self._measure_modes_avail = [self._special_measure_mode]
        hardware_measure_modes_avail = list(self._osc.measure_modes_available)
        for mode in hardware_measure_modes_avail:
            self._measure_modes_avail.append(mode)

        # halt the oscilloscope's measurement initially
        self._should_run = False

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
            self._mutex_dev_access.acquire()
            if self._osc.is_running or self._data_not_fetched_from_last_run:
                self._mutex_dev_access.release()

                self._data_not_fetched_from_last_run = False

                self._mutex_dev_access.acquire()

                # ensure that the oscilloscope is ready to have its data retrieved
                if self._osc.is_data_ready:

                    self._mutex_dev_access.release()

                    points = {}
                    min_voltage = None
                    max_voltage = None

                    frequency = [0]
                    min_share = None
                    max_share = None

                    # get the time vector from the oscilloscope
                    self._mutex_dev_access.acquire()
                    time = self._osc.time_vector
                    self._mutex_dev_access.release()

                    en_ch_numbers = []
                    raw_data = None

                    # retrieve the raw measurement data from the oscilloscope only if at least one channel is enabled
                    self._mutex_dev_access.acquire()
                    for i in range(self.ch_cnt):
                        if self._ch[i].is_enabled:
                            en_ch_numbers.append(i + 1)
                    if en_ch_numbers:
                        raw_data = self._osc.retrieve(en_ch_numbers)
                    self._mutex_dev_access.release()

                    self._mutex_running.release()

                    if raw_data is not None:
                        # convert the raw measurement data into QPoint arrays for each enabled channel
                        # and save both the minimum & maximum value
                        for i in range(len(en_ch_numbers)):
                            raw_channel_data = raw_data[en_ch_numbers[i] - 1]

                            # combine each element from the time vector and one channel's raw measurement data
                            # into a QPoint
                            current_norm_points = [QPointF(time[j], raw_channel_data[j]) for j in range(len(time))]

                            # calculate FFT
                            frequency, share = self.calculate_fft_points(time, raw_channel_data)
                            current_fft_points = [QPointF(frequency[j], share[j]) for j in range(len(frequency))]

                            # use the channel's number as key and the QPoint array tuple as value
                            points[en_ch_numbers[i]] = (current_norm_points, current_fft_points)

                            # set minimum and maximum across all channels
                            if min_voltage is None and max_voltage is None:
                                min_voltage = min(raw_channel_data)
                                max_voltage = max(raw_channel_data)
                            else:
                                min_voltage = min(min_voltage, min(raw_channel_data))
                                max_voltage = max(max_voltage, max(raw_channel_data))
                            if min_share is None and max_share is None:
                                min_share = min(share)
                                max_share = max(share)
                            else:
                                min_share = min(min_share, min(share))
                                max_share = max(max_share, max(share))

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
                    self._mutex_dev_access.release()
                    self._mutex_running.release()

            # restart the oscilloscope if it is currently in the special measure mode and should be running
            elif self._measure_mode == self._special_measure_mode and self._should_run:
                self._mutex_dev_access.release()
                all_channels_disabled = True

                self._mutex_dev_access.acquire()

                # only start the measurement if it has not already been started
                if not self._osc.is_running:

                    # ensure that at least one channel is enabled before starting the measurement
                    for ch in self._ch:
                        if ch.is_enabled:
                            all_channels_disabled = False
                            break
                    if not all_channels_disabled:
                        self._osc.start()
                        self._data_not_fetched_from_last_run = True
                    else:
                        self._should_run = False

                self._mutex_dev_access.release()
                self._mutex_running.release()

            else:
                self._should_run = False
                self._mutex_dev_access.release()
                self._mutex_running.release()

                # invoke the callback function to signal that the oscilloscope was stopped
                self._was_stopped(self._id)

                # halt the measurement while the oscilloscope is stopped
                with self._cond_running:
                    self._cond_running.wait()

    def _term_deletion(self):
        self._osc.dev_close()

    @property
    def is_running(self):
        self._mutex_dev_access.acquire()
        result = self._should_run
        self._mutex_dev_access.release()

        return result

    def start(self):
        success = False
        all_channels_disabled = True

        measure_mode = self.measure_mode

        # assert that the oscilloscope is not currently mid-measurement
        self._mutex_running.acquire()

        self._mutex_dev_access.acquire()

        # only start the measurement if it has not already been started
        if not self._osc.is_running:

            # ensure that at least one channel is enabled before starting the measurement
            for ch in self._ch:
                if ch.is_enabled:
                    all_channels_disabled = False
                    break
            if not all_channels_disabled:
                if measure_mode == 'block':
                    self._data_not_fetched_from_last_run = True

                self._osc.start()
                self._should_run = True
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
        if self._osc.is_running:
            self._osc.stop()
            self._should_run = False
            success = True
        elif self._measure_mode == self._special_measure_mode and self._should_run:
            self._should_run = False
            success = True

        self._mutex_dev_access.release()
        self._mutex_running.release()

        return success

    def force_trig(self):
        self._mutex_dev_access.acquire()

        # assert that trigger property can be accessed
        if self._osc.is_trig_available and self._osc.is_running:
            success = self._osc.force_trig()
        else:
            success = False

        self._mutex_dev_access.release()

        return success

    @property
    def measure_modes_avail(self):
        self._mutex_dev_access.acquire()
        result = self._measure_modes_avail
        self._mutex_dev_access.release()

        return result

    @property
    def measure_mode(self):
        self._mutex_dev_access.acquire()
        result = self._measure_mode
        self._mutex_dev_access.release()

        return result

    @measure_mode.setter
    def measure_mode(self, value):
        if value != self._special_measure_mode:
            self._mutex_dev_access.acquire()
            self._osc.measure_mode = value
            self._measure_mode = value
            self._mutex_dev_access.release()
        else:
            self._mutex_dev_access.acquire()
            self._osc.measure_mode = 'block'
            self._measure_mode = value
            self._mutex_dev_access.release()

    @property
    def auto_res_avail(self):
        self._mutex_dev_access.acquire()

        # convert tuple into list
        result = list(self._osc.auto_resolutions_available)

        self._mutex_dev_access.release()

        return result

    @property
    def auto_res(self):
        self._mutex_dev_access.acquire()
        result = self._osc.auto_resolution
        self._mutex_dev_access.release()

        return result

    @auto_res.setter
    def auto_res(self, value):
        self._mutex_dev_access.acquire()
        self._osc.auto_resolution = value
        self._mutex_dev_access.release()

    @property
    def res_avail(self):
        self._mutex_dev_access.acquire()

        # convert tuple into list
        result = list(self._osc.resolutions_available)

        self._mutex_dev_access.release()

        return result

    @property
    def res(self):
        self._mutex_dev_access.acquire()
        result = self._osc.resolution
        self._mutex_dev_access.release()

        return result

    @res.setter
    def res(self, value):
        self._mutex_dev_access.acquire()
        self._osc.resolution = value
        self._mutex_dev_access.release()

    @property
    def sample_freq_max(self):
        self._mutex_dev_access.acquire()
        result = self._osc.sample_freq_max
        self._mutex_dev_access.release()

        return result

    @property
    def sample_freq(self):
        self._mutex_dev_access.acquire()
        result = self._osc.sample_freq
        self._mutex_dev_access.release()

        return result

    @sample_freq.setter
    def sample_freq(self, value):
        # assert that minimum value is 1
        value = max(value, 1)

        self._mutex_dev_access.acquire()

        # assert that maximum value is not exceeded
        self._osc.sample_freq = min(value, self._osc.sample_freq_max)

        self._mutex_dev_access.release()

    @property
    def rec_len_max(self):
        self._mutex_dev_access.acquire()
        result = self._osc.record_length_max
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
        self._osc.record_length = min(value, self._osc.record_length_max)

        self._mutex_dev_access.release()

    @property
    def clock_src_avail(self):
        self._mutex_dev_access.acquire()

        # convert tuple into list
        result = list(self._osc.clock_sources_available)

        self._mutex_dev_access.release()

        return result

    @property
    def clock_src(self):
        self._mutex_dev_access.acquire()
        result = self._osc.clock_source
        self._mutex_dev_access.release()

        return result

    @clock_src.setter
    def clock_src(self, value):
        self._mutex_dev_access.acquire()
        self._osc.clock_source = value
        self._mutex_dev_access.release()

    @property
    def clock_outs_avail(self):
        self._mutex_dev_access.acquire()

        # convert tuple into list
        result = list(self._osc.clock_outputs_available)

        self._mutex_dev_access.release()

        return result

    @property
    def clock_out(self):
        self._mutex_dev_access.acquire()
        result = self._osc.clock_output
        self._mutex_dev_access.release()

        return result

    @clock_out.setter
    def clock_out(self, value):
        self._mutex_dev_access.acquire()
        self._osc.clock_output = value
        self._mutex_dev_access.release()

    @property
    def pre_sample_ratio(self):
        self._mutex_dev_access.acquire()

        # assert that trigger property can be accessed
        if self._osc.is_trig_available:
            result = self._osc.pre_sample_ratio
        else:
            result = '-'

        self._mutex_dev_access.release()

        return result

    @pre_sample_ratio.setter
    def pre_sample_ratio(self, value):
        # assert that value is within the minimum-maximum-range
        value = min(1, max(0, value))

        self._mutex_dev_access.acquire()

        # assert that trigger property can be accessed
        if self._osc.is_trig_available:
            self._osc.pre_sample_ratio = value

        self._mutex_dev_access.release()

    @property
    def seg_cnt_max(self):
        self._mutex_dev_access.acquire()

        # assert that oscilloscope property can be accessed
        if self._osc.is_trig_available:
            result = self._osc.segment_cnt_max
        else:
            result = 0

        self._mutex_dev_access.release()

        return result

    @property
    def seg_cnt(self):
        self._mutex_dev_access.acquire()

        # assert that oscilloscope property can be accessed
        if self._osc.is_trig_available:
            result = self._osc.segment_cnt
        else:
            result = 0

        self._mutex_dev_access.release()

        return result

    @seg_cnt.setter
    def seg_cnt(self, value):
        # assert that minimum value is 1
        value = max(value, 1)

        self._mutex_dev_access.acquire()

        # assert that oscilloscope property can be accessed
        if self._osc.is_trig_available:

            # assert that maximum value is not exceeded
            self._osc.segment_cnt = min(value, self._osc.segment_cnt_max)

        self._mutex_dev_access.release()

    @property
    def is_trig_avail(self):
        self._mutex_dev_access.acquire()
        result = self._osc.is_trig_available
        self._mutex_dev_access.release()

        return result

    @property
    def trig_timeout(self):
        self._mutex_dev_access.acquire()

        # assert that trigger property can be accessed
        if self._osc.is_trig_available:
            result = self._osc.trig_timeout
        else:
            result = '-'

        self._mutex_dev_access.release()

        return result

    @trig_timeout.setter
    def trig_timeout(self, value):
        # assert that the only possible negative value is -1
        if value < 0:
            value = -1

        self._mutex_dev_access.acquire()

        # assert that trigger property can be accessed
        if self._osc.is_trig_available:
            self._osc.trig_timeout = value

        self._mutex_dev_access.release()

    @property
    def trig_delay_max(self):
        self._mutex_dev_access.acquire()

        # assert that trigger property can be accessed
        if self._osc.is_trig_available:
            result = self._osc.trig_delay_max
        else:
            result = '-'

        self._mutex_dev_access.release()

        return result

    @property
    def trig_delay(self):
        self._mutex_dev_access.acquire()

        # assert that trigger property can be accessed
        if self._osc.is_trig_available:
            result = self._osc.trig_delay
        else:
            result = '-'

        self._mutex_dev_access.release()

        return result

    @trig_delay.setter
    def trig_delay(self, value):
        # assert that minimum value is 0
        value = max(value, 0)

        self._mutex_dev_access.acquire()

        # assert that trigger property can be accessed
        if self._osc.is_trig_available:

            # assert that maximum value is not exceeded
            self._osc.trig_delay = min(value, self._osc.trig_delay_max)

        self._mutex_dev_access.release()

    @property
    def trig_holdoff_max(self):
        self._mutex_dev_access.acquire()

        # assert that trigger property can be accessed
        if self._osc.is_trig_available:
            result = self._osc.trig_holdoff_max
        else:
            result = '-'

        self._mutex_dev_access.release()

        return result

    @property
    def trig_holdoff(self):
        self._mutex_dev_access.acquire()

        # assert that trigger property can be accessed
        if self._osc.is_trig_available:
            result = self._osc.trig_holdoff
        else:
            result = '-'

        self._mutex_dev_access.release()

        return result

    @trig_holdoff.setter
    def trig_holdoff(self, value):
        # assert that minimum value is 0
        value = max(value, 0)

        self._mutex_dev_access.acquire()

        # assert that trigger property can be accessed
        if self._osc.is_trig_available:

            # assert that maximum value is not exceeded
            self._osc.trig_holdoff = min(value, self._osc.trig_holdoff_max)

        self._mutex_dev_access.release()


class TiepieOscChannel(OscChannel):
    def __init__(self, name, ch_no, mutex, ch):
        """
        A TiePie engineering Handyscope channel interface, inherits from OscChannel.

        The interface connects to and communicates with an oscilloscope channel object from the "tiepie" library.
        This "tiepie" oscilloscope channel object is stored in a private attribute.

        Args:
            name (str):
                The moniker of the oscilloscope channel.
                Used for the 'Name' part of the channel's ID.
            ch_no (int):
                The number of the oscilloscope channel.
                Used for the 'No' part of the channel's ID.
            mutex (threading.Lock):
                The same threading lock that is used for every other property access to the associated device.
            ch (tiepie.oscilloscopeChannel.OscilloscopeChannel):
                The library-specific channel object which to interface with.

        Returns:
            TiepieOscChannel:
                A TiepieOscChannel object.
        """
        super().__init__(name, ch_no, mutex)

        # save the library-specific channel object
        self._ch = ch

        # set trigger level mode to 'absolute' instead of 'relative'
        self._ch.trig_lvl_mode = 'absolute'

        # disable the channel initially
        self._ch.is_enabled = False

    @OscChannel.is_enabled.setter
    def is_enabled(self, value):
        self._mutex_dev_access.acquire()
        self._ch.is_enabled = value
        self._is_enabled = value
        self._mutex_dev_access.release()

    @property
    def is_avail(self):
        self._mutex_dev_access.acquire()
        result = self._ch.is_available
        self._mutex_dev_access.release()

        return result

    @property
    def couplings_avail(self):
        self._mutex_dev_access.acquire()

        # convert tuple into list
        result = list(self._ch.couplings_available)

        self._mutex_dev_access.release()

        return result

    @property
    def coupling(self):
        self._mutex_dev_access.acquire()
        result = self._ch.coupling
        self._mutex_dev_access.release()

        return result

    @coupling.setter
    def coupling(self, value):
        self._mutex_dev_access.acquire()
        self._ch.coupling = value
        self._mutex_dev_access.release()

    @property
    def probe_gain(self):
        self._mutex_dev_access.acquire()
        result = self._ch.probe_gain
        self._mutex_dev_access.release()

        return result

    @probe_gain.setter
    def probe_gain(self, value):
        # assert that value is non-zero and within the minimum-maximum-range
        if value == 0:
            value = 1
        else:
            value = min(1000000, max(-1000000, value))

        self._mutex_dev_access.acquire()
        self._ch.probe_gain = value
        self._mutex_dev_access.release()

    @property
    def probe_offset(self):
        self._mutex_dev_access.acquire()
        result = self._ch.probe_offset
        self._mutex_dev_access.release()

        return result

    @probe_offset.setter
    def probe_offset(self, value):
        # assert that value is within the minimum-maximum-range
        value = min(1000000, max(-1000000, value))

        self._mutex_dev_access.acquire()
        self._ch.probe_offset = value
        self._mutex_dev_access.release()

    @property
    def is_auto_range(self):
        self._mutex_dev_access.acquire()
        result = self._ch.is_auto_range
        self._mutex_dev_access.release()

        return result

    @is_auto_range.setter
    def is_auto_range(self, value):
        self._mutex_dev_access.acquire()

        # assert that trigger property can be accessed
        if self._ch.is_trig_available:
            self._ch.is_auto_range = value

        self._mutex_dev_access.release()

    @property
    def ranges_avail(self):
        self._mutex_dev_access.acquire()

        # convert tuple into list
        result = list(self._ch.ranges_available)

        self._mutex_dev_access.release()

        return result

    @property
    def range(self):
        self._mutex_dev_access.acquire()
        result = self._ch.range
        self._mutex_dev_access.release()

        return result

    @range.setter
    def range(self, value):
        self._mutex_dev_access.acquire()
        self._ch.range = value
        self._mutex_dev_access.release()

    @property
    def is_trig_avail(self):
        self._mutex_dev_access.acquire()
        result = self._ch.is_trig_available
        self._mutex_dev_access.release()

        return result

    @property
    def is_trig_enabled(self):
        self._mutex_dev_access.acquire()

        # assert that trigger property can be accessed
        if self._ch.is_trig_available:
            result = self._ch.is_trig_enabled
        else:
            result = False

        self._mutex_dev_access.release()

        return result

    @is_trig_enabled.setter
    def is_trig_enabled(self, value):
        self._mutex_dev_access.acquire()

        # assert that trigger property can be accessed
        if self._ch.is_trig_available:
            self._ch.is_trig_enabled = value

        self._mutex_dev_access.release()

    @property
    def trig_kinds_avail(self):
        self._mutex_dev_access.acquire()

        # assert that trigger property can be accessed
        if self._ch.is_trig_available:

            # convert tuple into list
            result = list(self._ch.trig_kinds_available)

        else:
            result = ['-']

        self._mutex_dev_access.release()

        return result

    @property
    def trig_kind(self):
        self._mutex_dev_access.acquire()

        # assert that trigger property can be accessed
        if self._ch.is_trig_available:
            result = self._ch.trig_kind
        else:
            result = '-'

        self._mutex_dev_access.release()

        return result

    @trig_kind.setter
    def trig_kind(self, value):
        self._mutex_dev_access.acquire()

        # assert that trigger property can be accessed
        if self._ch.is_trig_available:
            self._ch.trig_kind = value

        self._mutex_dev_access.release()

    @property
    def trig_lvl_cnt(self):
        self._mutex_dev_access.acquire()

        # assert that trigger property can be accessed
        if self._ch.is_trig_available:
            result = self._ch.trig_lvl_cnt
        else:
            result = 0

        self._mutex_dev_access.release()

        return result

    @property
    def trig_lvl(self):
        self._mutex_dev_access.acquire()

        # assert that trigger property can be accessed
        if self._ch.is_trig_available:

            # convert tuple into list
            result = list(self._ch.trig_lvl)

        else:
            result = ['-']

        self._mutex_dev_access.release()

        return result

    @trig_lvl.setter
    def trig_lvl(self, value):
        self._mutex_dev_access.acquire()

        # assert that trigger property can be accessed
        if self._ch.is_trig_available:

            # assert that maximum amount of applicable values is not exceeded
            value = value[:self._ch.trig_lvl_cnt]

            self._ch.trig_lvl = value

        self._mutex_dev_access.release()

    @property
    def trig_hyst_cnt(self):
        self._mutex_dev_access.acquire()

        # assert that trigger property can be accessed
        if self._ch.is_trig_available:
            result = self._ch.trig_hysteresis_cnt
        else:
            result = 0

        self._mutex_dev_access.release()

        return result

    @property
    def trig_hyst(self):
        self._mutex_dev_access.acquire()

        # assert that trigger property can be accessed
        if self._ch.is_trig_available:

            # hysteresis can't be set in 'in window' and 'out window' mode
            if self._ch.trig_kind != 'in window' and self._ch.trig_kind != 'out window':
                # convert tuple into list
                result = list(self._ch.trig_hysteresis)
            else:
                result = [(max(self._ch.trig_lvl) - min(self._ch.trig_lvl)) / self._ch.range]

        else:
            result = ['-']

        self._mutex_dev_access.release()

        return result

    @trig_hyst.setter
    def trig_hyst(self, value):
        self._mutex_dev_access.acquire()

        # assert that trigger property can be accessed
        if self._ch.is_trig_available:

            # hysteresis can't be set in 'in window' and 'out window' mode
            if self._ch.trig_kind != 'in window' and self._ch.trig_kind != 'out window':
                # assert that maximum amount of applicable values is not exceeded
                value = value[:self._ch.trig_hysteresis_cnt]

                # assert that each value is within the minimum-maximum-range
                for i in range(len(value)):
                    value[i] = min(1, max(0, value[i]))

                self._ch.trig_hysteresis = value
            else:
                self._ch.trig_lvl = [max(self._ch.trig_lvl), max(self._ch.trig_lvl)-value[0]*self._ch.range]

        self._mutex_dev_access.release()

    @property
    def trig_cond_avail(self):
        self._mutex_dev_access.acquire()

        # assert that trigger property can be accessed
        if self._ch.is_trig_available and self._ch.trig_kind not in ["rising", "falling", "any"]:

            # convert tuple into list
            result = list(self._ch.trig_conditions_available)

        else:
            result = ['-']

        self._mutex_dev_access.release()

        return result

    @property
    def trig_cond(self):
        self._mutex_dev_access.acquire()

        # assert that trigger property can be accessed
        if self._ch.is_trig_available and self._ch.trig_kind not in ["rising", "falling", "any"]:
            result = self._ch.trig_condition
        else:
            result = '-'

        self._mutex_dev_access.release()

        return result

    @trig_cond.setter
    def trig_cond(self, value):
        self._mutex_dev_access.acquire()

        # assert that trigger property can be accessed
        if self._ch.is_trig_available and self._ch.trig_kind not in ["rising", "falling", "any"]:
            self._ch.trig_condition = value

        self._mutex_dev_access.release()

    @property
    def trig_time_cnt(self):
        self._mutex_dev_access.acquire()

        # assert that trigger property can be accessed
        if self._ch.is_trig_available and self._ch.trig_kind not in ["rising", "falling", "any"]:
            result = self._ch.trig_time_cnt
        else:
            result = 0

        self._mutex_dev_access.release()

        return result

    @property
    def trig_time(self):
        self._mutex_dev_access.acquire()

        # assert that trigger property can be accessed
        if self._ch.is_trig_available \
                and self._ch.trig_kind not in ["rising", "falling", "any"] and self._ch.trig_condition != "none":
            result = list(self._ch.trig_time)
        else:
            result = ['-']

        self._mutex_dev_access.release()

        return result

    @trig_time.setter
    def trig_time(self, value):
        self._mutex_dev_access.acquire()

        # assert that trigger property can be accessed
        if self._ch.is_trig_available \
                and self._ch.trig_kind not in ["rising", "falling", "any"] and self._ch.trig_condition != "none":

            # assert that maximum amount of applicable values is not exceeded
            value = value[:self._ch.trig_time_cnt]

            # assert that each value is within the minimum-maximum-range
            for i in range(len(value)):
                value[i] = min(1, max(0, value[i]))

            self._ch.trig_time = value
        self._mutex_dev_access.release()
