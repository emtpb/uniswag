import tiepie

from uniswag.devices.generator import Generator, GenChannel


class TiepieGen(Generator):
    def __init__(self, name, ser_no):
        """
        A TiePie engineering Handyscope interface, inherits from Generator.

        The interface connects to and communicates with a generator object from the "tiepie" library.
        This "tiepie" generator object is stored in a private attribute.

        Args:
            name (str):
                The moniker of the generator.
                Used for the 'Name' part of the device's ID.
            ser_no (str):
                The serial number of the generator.
                Used for the 'SerNo' part of the device's ID.

        Returns:
            TiepieGen:
                A TiepieGen object.
        """
        super().__init__('Tiepie', name, ser_no)

        # create the library-specific generator object which to interface with
        self._gen = tiepie.Generator(instr_id=int(ser_no), id_kind='serial number')

        # fill the generator's channel list
        self._ch.append(TiepieGenChannel('Channel', 1, self._mutex_dev_access, self._gen))

        # halt the signal generation initially
        self._is_running = False

    def _term_deletion(self):
        self._gen.dev_close()

    @property
    def is_running(self):
        self._mutex_dev_access.acquire()
        result = self._is_running
        self._mutex_dev_access.release()

        return result

    def start(self):
        success = False
        all_channels_disabled = True

        self._mutex_dev_access.acquire()

        # assert that generator property can be accessed
        if self._gen.is_controllable and not self._is_running:

            # ensure that at least one channel is enabled before starting the measurement
            for ch in self._ch:
                if ch.is_enabled:
                    all_channels_disabled = False
                    break
            if not all_channels_disabled:
                self._gen.start()
                self._is_running = True
                success = True

        self._mutex_dev_access.release()

        return success

    def stop(self):
        success = False

        self._mutex_dev_access.acquire()

        # assert that generator property can be accessed
        if self._gen.is_controllable and self._is_running:
            self._gen.stop()
            self._is_running = False
            success = True

        self._mutex_dev_access.release()

        return success


class TiepieGenChannel(GenChannel):
    def __init__(self, name, ch_no, mutex, gen):
        """
        A TiePie engineering Handyscope channel interface, inherits from GenChannel.

        The interface connects to and communicates with a generator object from the "tiepie" library.
        This "tiepie" generator object is stored in a private attribute.

        Args:
            name (str):
                The moniker of the generator channel.
                Used for the 'Name' part of the channel's ID.
            ch_no (int):
                The number of the generator channel.
                Used for the 'No' part of the channel's ID.
            mutex (threading.Lock):
                The same threading lock that is used for every other property access to the associated device.
            gen (tiepie.Generator):
                The library-specific generator object which to interface with.

        Returns:
            TiepieGenChannel:
                A TiepieGenChannel object.
        """
        super().__init__(name, ch_no, mutex)

        # save the library-specific generator object
        self._ch = gen

        # disable the channel initially
        self._ch.is_out_on = False

        # the vector of the raw arbitrary signal samples that is uploaded into the device's waveform buffer
        self._raw_arb_data = [0]

        # initialize all the attributes that influence the signal preview graph
        self._update_preview_variables()

    def _update_preview_variables(self):
        self._mutex_preview_variables.acquire()

        sig_type = self._ch.signal_type
        if sig_type == 'sine':
            self._signal_type = 'sine'
        elif sig_type == 'triangle':
            self._signal_type = 'ramp'
        elif sig_type == 'square':
            self._signal_type = 'square'
        elif sig_type == 'pulse':
            self._signal_type = 'pulse'
        elif sig_type == 'arbitrary':
            self._signal_type = 'arbitrary'
        else:
            self._signal_type = 'unknown'

        self._offset = self._ch.offset

        # functionalities that are not available with certain settings / certain TiePie models
        try:
            self._amplitude = self._ch.amplitude
        except OSError:
            pass
        try:
            self._period = 1 / self._ch.freq
        except OSError:
            pass
        try:
            self._phase = self._ch.phase
        except OSError:
            pass
        try:
            self._symmetry = self._ch.symmetry
        except OSError:
            pass
        try:
            self._duty_cycle = self._ch.pulse_width / self._period
        except OSError:
            pass

        try:

            # calculate new content of the waveform buffer (after the device applied normalization etc.)
            limit = max(abs(min(self._raw_arb_data)), abs(max(self._raw_arb_data)))
            if limit != 0:
                normalizing_factor = self._amplitude / limit
            else:
                normalizing_factor = 0
            normalized_values = [entry * normalizing_factor + self._offset for entry in self._raw_arb_data]
            self._arbitrary_data[1] = normalized_values

            # calculate the time vector associated with the waveform buffer's content
            time_vector = []
            time_value = 0
            number_of_samples = len(self._raw_arb_data)
            if self._ch.freq_mode == 'signal':
                time_difference = self._period / number_of_samples
            else:
                time_difference = self._period
            for _ in range(number_of_samples):
                time_vector.append(time_value)
                time_value += time_difference
            self._arbitrary_data[0] = time_vector

        except OSError:
            pass

        self._mutex_preview_variables.release()

    @GenChannel.is_enabled.setter
    def is_enabled(self, value):
        self._mutex_dev_access.acquire()

        # assert that generator property can be accessed
        if self._ch.is_controllable:
            self._ch.is_out_on = value
            self._is_enabled = value

        self._mutex_dev_access.release()

    def arb_data(self, value):
        success = False

        self._mutex_dev_access.acquire()

        # assert that generator property can be accessed
        if self._ch.is_controllable and self._ch.signal_type == 'arbitrary':

            # ensure the minimum vector length
            if len(value) >= self._ch.arb_data_length_min:

                # assert that maximum amount of applicable values is not exceeded
                value = value[:self._ch.arb_data_length_max]

                self._ch.arb_data(value)
                self._raw_arb_data = value
                self._update_preview_variables()

                success = True

        self._mutex_dev_access.release()

        return success

    @property
    def is_out_inv(self):
        self._mutex_dev_access.acquire()
        result = self._ch.is_out_inv
        self._mutex_dev_access.release()

        return result

    @is_out_inv.setter
    def is_out_inv(self, value):
        self._mutex_dev_access.acquire()

        # assert that generator property can be accessed
        if self._ch.is_controllable:
            self._ch.is_out_inv = value

        self._mutex_dev_access.release()

    @property
    def sig_types_avail(self):
        self._mutex_dev_access.acquire()

        # convert tuple into list
        result = list(self._ch.signal_types_available)

        self._mutex_dev_access.release()

        return result

    @property
    def sig_type(self):
        self._mutex_dev_access.acquire()
        result = self._ch.signal_type
        self._mutex_dev_access.release()

        return result

    @sig_type.setter
    def sig_type(self, value):
        self._mutex_dev_access.acquire()

        # assert that generator property can be accessed
        if self._ch.is_controllable:
            self._ch.signal_type = value
            self._update_preview_variables()

        self._mutex_dev_access.release()

    @property
    def amp(self):
        self._mutex_dev_access.acquire()

        # assert that generator property can be accessed
        if self._ch.signal_type not in ['DC']:
            result = self._ch.amplitude
        else:
            result = '-'

        self._mutex_dev_access.release()

        return result

    @amp.setter
    def amp(self, value):
        self._mutex_dev_access.acquire()

        # assert that generator property can be accessed
        if self._ch.is_controllable and self._ch.signal_type not in ['DC']:

            # assert that value is within the minimum-maximum-range
            value = min(self._ch.amplitude_max, max(self._ch.amplitude_min, value))

            self._ch.amplitude = value
            self._update_preview_variables()

        self._mutex_dev_access.release()

    @property
    def amp_ranges_avail(self):
        self._mutex_dev_access.acquire()

        # convert tuple into list
        result = list(self._ch.amplitude_ranges_available)

        self._mutex_dev_access.release()

        return result

    @property
    def amp_range(self):
        self._mutex_dev_access.acquire()
        result = self._ch.amplitude_range
        self._mutex_dev_access.release()

        return result

    @amp_range.setter
    def amp_range(self, value):
        self._mutex_dev_access.acquire()

        # assert that generator property can be accessed
        if self._ch.is_controllable:
            self._ch.amplitude_range = value

        self._mutex_dev_access.release()

    @property
    def is_amp_auto_range(self):
        self._mutex_dev_access.acquire()
        result = self._ch.is_amplitude_autorange
        self._mutex_dev_access.release()

        return result

    @is_amp_auto_range.setter
    def is_amp_auto_range(self, value):
        self._mutex_dev_access.acquire()

        # assert that generator property can be accessed
        if self._ch.is_controllable:
            self._ch.is_amplitude_autorange = value

        self._mutex_dev_access.release()

    @property
    def offset(self):
        self._mutex_dev_access.acquire()
        result = self._ch.offset
        self._mutex_dev_access.release()

        return result

    @offset.setter
    def offset(self, value):
        self._mutex_dev_access.acquire()

        # assert that generator property can be accessed
        if self._ch.is_controllable:

            # assert that value is within the minimum-maximum-range
            value = min(self._ch.offset_max, max(self._ch.offset_min, value))

            self._ch.offset = value
            self._update_preview_variables()

        self._mutex_dev_access.release()

    @property
    def freq(self):
        self._mutex_dev_access.acquire()

        # assert that generator property can be accessed
        if self._ch.signal_type not in ['DC']:
            result = self._ch.freq
        else:
            result = '-'

        self._mutex_dev_access.release()

        return result

    @freq.setter
    def freq(self, value):
        self._mutex_dev_access.acquire()

        # assert that generator property can be accessed
        if self._ch.is_controllable and self._ch.signal_type not in ['DC']:

            # assert that value is within the minimum-maximum-range
            value = min(self._ch.freq_max, max(self._ch.freq_min, value))

            self._ch.freq = value
            self._update_preview_variables()

        self._mutex_dev_access.release()

    @property
    def freq_modes_avail(self):
        self._mutex_dev_access.acquire()

        # assert that generator property can be accessed
        if self._ch.signal_type not in ['DC', 'noise']:

            # convert tuple into list
            result = list(self._ch.freq_modes_available)

        else:
            result = ['-']

        self._mutex_dev_access.release()

        return result

    @property
    def freq_mode(self):
        self._mutex_dev_access.acquire()

        # assert that generator property can be accessed
        if self._ch.signal_type not in ['DC', 'noise']:
            result = self._ch.freq_mode
        else:
            result = '-'

        self._mutex_dev_access.release()

        return result

    @freq_mode.setter
    def freq_mode(self, value):
        self._mutex_dev_access.acquire()

        # assert that generator property can be accessed
        if self._ch.is_controllable and self._ch.signal_type not in ['DC', 'noise']:
            self._ch.freq_mode = value
            self._update_preview_variables()

        self._mutex_dev_access.release()

    @property
    def phase(self):
        self._mutex_dev_access.acquire()
        result = self._ch.phase
        self._mutex_dev_access.release()

        return result

    @phase.setter
    def phase(self, value):
        self._mutex_dev_access.acquire()

        # assert that generator property can be accessed
        if self._ch.is_controllable:

            # assert that value is within the minimum-maximum-range
            value = min(self._ch.phase_max, max(self._ch.phase_min, value))

            self._ch.phase = value
            self._update_preview_variables()

        self._mutex_dev_access.release()

    @property
    def symmetry(self):
        self._mutex_dev_access.acquire()

        # assert that generator property can be accessed
        if self._ch.signal_type not in ['DC', 'noise', 'arbitrary']:
            result = self._ch.symmetry
        else:
            result = '-'

        self._mutex_dev_access.release()

        return result

    @symmetry.setter
    def symmetry(self, value):
        self._mutex_dev_access.acquire()

        # assert that generator property can be accessed
        if self._ch.is_controllable and self._ch.signal_type not in ['DC', 'noise', 'arbitrary']:

            # assert that value is within the minimum-maximum-range
            value = min(self._ch.symmetry_max, max(self._ch.symmetry_min, value))

            self._ch.symmetry = value
            self._update_preview_variables()

        self._mutex_dev_access.release()

    @property
    def pulse_width(self):
        self._mutex_dev_access.acquire()
        result = self._ch.pulse_width
        self._mutex_dev_access.release()

        return result

    @pulse_width.setter
    def pulse_width(self, value):
        self._mutex_dev_access.acquire()

        # assert that generator property can be accessed
        if self._ch.is_controllable:

            # assert that value is within the minimum-maximum-range
            value = min(self._ch.pulse_width_max, max(self._ch.pulse_width_min, value))

            self._ch.pulse_width = value
            self._update_preview_variables()

        self._mutex_dev_access.release()

    @property
    def modes_avail(self):
        self._mutex_dev_access.acquire()

        # convert tuple into list
        result = list(self._ch.modes_available)

        self._mutex_dev_access.release()

        return result

    @property
    def mode(self):
        self._mutex_dev_access.acquire()
        result = self._ch.mode
        self._mutex_dev_access.release()

        return result

    @mode.setter
    def mode(self, value):
        self._mutex_dev_access.acquire()

        # assert that generator property can be accessed
        if self._ch.is_controllable:
            self._ch.mode = value

        self._mutex_dev_access.release()

    @property
    def burst_cnt(self):
        self._mutex_dev_access.acquire()

        # assert that burst property can be accessed
        if self._ch.mode == 'burst count':
            result = self._ch.burst_cnt
        else:
            result = '-'

        self._mutex_dev_access.release()

        return result

    @burst_cnt.setter
    def burst_cnt(self, value):
        self._mutex_dev_access.acquire()

        # assert that burst & generator property can be accessed
        if self._ch.mode == 'burst count' and self._ch.is_controllable:

            # assert that value is within the minimum-maximum-range
            value = min(self._ch.burst_cnt_max, max(self._ch.burst_cnt_min, value))

            self._ch.burst_cnt = value

        self._mutex_dev_access.release()

    @property
    def burst_sample_cnt(self):
        self._mutex_dev_access.acquire()
        result = self._ch.burst_sample_cnt
        self._mutex_dev_access.release()

        return result

    @burst_sample_cnt.setter
    def burst_sample_cnt(self, value):
        self._mutex_dev_access.acquire()

        # assert that generator property can be accessed
        if self._ch.is_controllable:

            # assert that value is within the minimum-maximum-range
            value = min(self._ch.burst_sample_cnt_max, max(self._ch.burst_sample_cnt_min, value))

            self._ch.burst_sample_cnt = value

        self._mutex_dev_access.release()

    @property
    def burst_seg_cnt(self):
        self._mutex_dev_access.acquire()
        result = self._ch.burst_sample_cnt
        self._mutex_dev_access.release()

        return result

    @burst_seg_cnt.setter
    def burst_seg_cnt(self, value):
        self._mutex_dev_access.acquire()

        # assert that generator property can be accessed
        if self._ch.is_controllable:

            # assert that value is within the minimum-maximum-range
            value = min(self._ch.burst_segment_cnt_max, max(self._ch.burst_segment_cnt_min, value))

            self._ch.burst_segment_cnt = value

        self._mutex_dev_access.release()
