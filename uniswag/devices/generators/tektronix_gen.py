import math
import time

import numpy as np
import tektronixsg
import tektronixsg.channel

from uniswag.devices.generator import Generator, GenChannel


class TektronixGen(Generator):
    def __init__(self, name, ser_no):
        """
        A Tektronix Arbitrary Function Generator interface, inherits from Generator.

        The interface connects to and communicates with a signal generator object from the "tektronixsg" library.
        This "tektronixsg" signal generator object is stored in a private attribute.

        Args:
            name (str):
                The moniker of the generator.
                Used for the 'Name' part of the device's ID.
            ser_no (str):
                The serial number of the generator.
                Used for the 'SerNo' part of the device's ID.

        Returns:
            TektronixGen:
                A TektronixGen object.
        """
        super().__init__('Tektronix', name, ser_no)

        # create the library-specific generator object which to interface with
        res = self._get_resource_from_ser_no()
        self._gen = tektronixsg.SignalGenerator(resource=res)

        # reset the device initially to synchronize the device's state with the software's state
        self._gen.reset()

        # fill the generator's channel list
        i = 0
        for channel_obj in self._gen.channels:
            self._ch.append(TektronixGenChannel('Channel', i + 1, self._mutex_dev_access, channel_obj))
            i += 1

    def _get_resource_from_ser_no(self):
        devices = tektronixsg.list_connected_devices()
        ser_no = self._id["SerNo"]
        for device in devices:
            if ser_no == device.split('::')[3]:
                return device
        return None

    def _term_deletion(self):
        self._gen.close()

    @property
    def is_running(self):
        return True

    def start(self):
        return False

    def stop(self):
        return False

    def reset(self):
        self._mutex_dev_access.acquire()
        self._gen.reset()
        for channel in self._ch:
            channel.reset_preview_variables()
        self._mutex_dev_access.release()

    def force_trig(self):
        self._mutex_dev_access.acquire()
        self._gen.send_trigger()
        self._mutex_dev_access.release()

        return True

    @staticmethod
    def trig_src_avail():
        result = list(tektronixsg.generator.TRIGGER_SOURCE.keys())
        return result

    @property
    def trig_src(self):
        self._mutex_dev_access.acquire()
        result = self._gen.trigger_source
        self._mutex_dev_access.release()

        return result

    @trig_src.setter
    def trig_src(self, value):
        self._mutex_dev_access.acquire()
        self._gen.trigger_source = value
        self._mutex_dev_access.release()

    @property
    def trig_time(self):
        self._mutex_dev_access.acquire()
        result = self._gen.trigger_timer
        self._mutex_dev_access.release()

        return result

    @trig_time.setter
    def trig_time(self, value):
        self._mutex_dev_access.acquire()
        self._gen.trigger_timer = value
        self._mutex_dev_access.release()


class TektronixGenChannel(GenChannel):
    def __init__(self, name, ch_no, mutex, ch):
        """
        A Tektronix Arbitrary Function Generator channel interface, inherits from GenChannel.

        The interface connects to and communicates with a channel object from the "tektronixsg" library.
        This "tektronixsg" channel object is stored in a private attribute.

        Args:
            name (str):
                The moniker of the generator channel.
                Used for the 'Name' part of the channel's ID.
            ch_no (int):
                The number of the generator channel.
                Used for the 'No' part of the channel's ID.
            mutex (threading.Lock):
                The same threading lock that is used for every other property access to the associated device.
            ch (tektronixsg.channel.Channel):
                The library-specific channel object which to interface with.

        Returns:
            TektronixGenChannel:
                A TektronixGenChannel object.
        """
        super().__init__(name, ch_no, mutex)

        # save the library-specific channel object
        self._ch = ch

        # define available signal types
        if self._ch.generator.connected_device == "AFG1022":
            self._sig_types_avail = list(tektronixsg.channel.SIGNAL_TYPES_AFG1022.keys())
        elif self._ch.generator.connected_device == "AFG31052":
            self._sig_types_avail = list(tektronixsg.channel.SIGNAL_TYPES_AFG31000.keys())
        else:
            self._sig_types_avail = ['-']

        # initialize all the attributes that influence the signal preview graph
        self._update_preview_variables()

    def _update_preview_variables(self):
        self._mutex_preview_variables.acquire()

        sig_type = self._ch.signal_type
        if sig_type == 'sine':
            self._signal_type = 'sine'
        elif sig_type == 'ramp':
            self._signal_type = 'ramp'
        elif sig_type == 'square':
            self._signal_type = 'square'
        elif sig_type == 'pulse':
            self._signal_type = 'pulse'
        elif sig_type[:-1] == 'memory':
            self._signal_type = 'arbitrary'
        else:
            self._signal_type = 'unknown'

        self._offset = self._ch.voltage_offset
        self._amplitude = self._ch.voltage_amplitude / 2
        self._period = self._ch.pulse_period
        self._phase = math.degrees(self._ch.phase)
        self._duty_cycle = self._ch.pulse_duty * 0.01

        # no VISA commands defined by Tektronix to set/query symmetry
        self._symmetry = 0.5

        # get new content of the waveform buffer (after the device applied normalization etc.)
        raw_arb_data = self._ch.generator.read_data_emom(self._id['No'])
        normalizing_factor = ((self._offset + self._amplitude) - (self._offset - self._amplitude)) / 16383
        normalized_values = [entry * normalizing_factor + (self._offset - self._amplitude) for entry in raw_arb_data]
        self._arbitrary_data[1] = normalized_values

        # calculate the time vector associated with the waveform buffer's content
        time_vector = []
        time_value = 0
        number_of_samples = len(self._arbitrary_data[1])
        for _ in range(number_of_samples):
            time_vector.append(time_value)
            time_value += self._period / number_of_samples
        self._arbitrary_data[0] = time_vector

        self._mutex_preview_variables.release()

    @GenChannel.is_enabled.setter
    def is_enabled(self, value):
        self._mutex_dev_access.acquire()

        self._ch.output_on = value
        self._is_enabled = value

        self._mutex_dev_access.release()

    def reset_preview_variables(self):
        self._update_preview_variables()

    def arb_data(self, value):
        success = False

        # ensure the minimum vector length
        if len(value) >= 2:

            # assert that maximum amount of applicable values is not exceeded
            value = value[:8192]

            value = np.array(value)

            self._mutex_dev_access.acquire()

            # from the set_arbitrary_signal function
            min_voltage = min(value)
            max_voltage = max(value)
            voltage_range = abs(max_voltage - min_voltage)
            normed_voltage = abs(value - min_voltage) / voltage_range
            tmp = 16383 * normed_voltage
            voltage_bits = tmp.astype(int)
            self._ch.generator.write_data_emom(voltage_bits, self._id['No'])
            time.sleep(0.2)

            # self._ch.set_arbitrary_signal(value)
            self._update_preview_variables()

            self._mutex_dev_access.release()

            success = True

        return success

    @property
    def volt_max(self):
        self._mutex_dev_access.acquire()
        result = self._ch.voltage_max
        self._mutex_dev_access.release()

        return result

    @volt_max.setter
    def volt_max(self, value):
        self._mutex_dev_access.acquire()
        self._ch.voltage_max = value
        self._update_preview_variables()
        self._mutex_dev_access.release()

    @property
    def volt_min(self):
        self._mutex_dev_access.acquire()
        result = self._ch.voltage_min
        self._mutex_dev_access.release()

        return result

    @volt_min.setter
    def volt_min(self, value):
        self._mutex_dev_access.acquire()
        self._ch.voltage_min = value
        self._update_preview_variables()
        self._mutex_dev_access.release()

    @property
    def offset(self):
        self._mutex_dev_access.acquire()
        result = self._ch.voltage_offset
        self._mutex_dev_access.release()

        return result

    @offset.setter
    def offset(self, value):
        self._mutex_dev_access.acquire()
        self._ch.voltage_offset = value
        self._update_preview_variables()
        self._mutex_dev_access.release()

    @property
    def amp(self):
        self._mutex_dev_access.acquire()
        result = self._ch.voltage_amplitude
        self._mutex_dev_access.release()

        return result

    @amp.setter
    def amp(self, value):
        self._mutex_dev_access.acquire()
        self._ch.voltage_amplitude = value
        self._update_preview_variables()
        self._mutex_dev_access.release()

    @property
    def sig_types_avail(self):
        result = self._sig_types_avail
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
        self._ch.signal_type = value
        self._update_preview_variables()
        self._mutex_dev_access.release()

    @property
    def impedance(self):
        self._mutex_dev_access.acquire()
        result = self._ch.impedance
        self._mutex_dev_access.release()

        return result

    @impedance.setter
    def impedance(self, value):
        self._mutex_dev_access.acquire()
        self._ch.impedance = value
        self._update_preview_variables()
        self._mutex_dev_access.release()

    @property
    def freq(self):
        self._mutex_dev_access.acquire()
        result = self._ch.frequency
        self._mutex_dev_access.release()

        return result

    @freq.setter
    def freq(self, value):
        self._mutex_dev_access.acquire()
        self._ch.frequency = value
        self._update_preview_variables()
        self._mutex_dev_access.release()

    @property
    def phase(self):
        self._mutex_dev_access.acquire()
        result = math.degrees(self._ch.phase)
        self._mutex_dev_access.release()

        return result

    @phase.setter
    def phase(self, value):
        self._mutex_dev_access.acquire()
        self._ch.phase = math.radians(value)
        self._update_preview_variables()
        self._mutex_dev_access.release()

    @property
    def is_burst_on(self):
        self._mutex_dev_access.acquire()

        # property can be inaccessible for certain channels of certain models
        try:
            result = self._ch.burst_on
        except NotImplementedError:
            result = False

        self._mutex_dev_access.release()

        return result

    @is_burst_on.setter
    def is_burst_on(self, value):
        self._mutex_dev_access.acquire()

        # property can be inaccessible for certain channels of certain models
        try:
            self._ch.burst_on = value
        except NotImplementedError:
            pass

        self._mutex_dev_access.release()

    @staticmethod
    def burst_modes_avail():
        result = list(tektronixsg.channel.BURST_MODE.keys())
        return result

    @property
    def burst_mode(self):
        self._mutex_dev_access.acquire()

        # property can be inaccessible for certain channels of certain models
        try:
            result = self._ch.burst_mode
        except NotImplementedError:
            result = '-'

        self._mutex_dev_access.release()

        return result

    @burst_mode.setter
    def burst_mode(self, value):
        self._mutex_dev_access.acquire()

        # property can be inaccessible for certain channels of certain models
        try:
            self._ch.burst_mode = value
        except NotImplementedError:
            pass

        self._mutex_dev_access.release()

    @property
    def burst_cnt(self):
        self._mutex_dev_access.acquire()

        # property can be inaccessible for certain channels of certain models
        try:
            result = self._ch.burst_cycles
        except NotImplementedError:
            result = '-'

        self._mutex_dev_access.release()

        return result

    @burst_cnt.setter
    def burst_cnt(self, value):
        self._mutex_dev_access.acquire()

        # property can be inaccessible for certain channels of certain models
        try:
            self._ch.burst_cycles = value
        except NotImplementedError:
            pass

        self._mutex_dev_access.release()

    @property
    def burst_delay(self):
        self._mutex_dev_access.acquire()
        result = self._ch.burst_delay
        self._mutex_dev_access.release()

        return result

    @burst_delay.setter
    def burst_delay(self, value):
        self._mutex_dev_access.acquire()
        self._ch.burst_delay = value
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
        self._ch.pulse_width = value
        self._update_preview_variables()
        self._mutex_dev_access.release()

    @property
    def duty_cycle(self):
        self._mutex_dev_access.acquire()
        result = self._ch.pulse_duty * 0.01
        self._mutex_dev_access.release()

        return result

    @duty_cycle.setter
    def duty_cycle(self, value):
        self._mutex_dev_access.acquire()
        self._ch.pulse_duty = value * 100
        self._update_preview_variables()
        self._mutex_dev_access.release()

    @property
    def pulse_delay(self):
        self._mutex_dev_access.acquire()
        result = self._ch.pulse_delay
        self._mutex_dev_access.release()

        return result

    @pulse_delay.setter
    def pulse_delay(self, value):
        self._mutex_dev_access.acquire()
        self._ch.pulse_delay = value
        self._mutex_dev_access.release()

    @property
    def pulse_hold(self):
        self._mutex_dev_access.acquire()
        result = self._ch.pulse_hold
        self._mutex_dev_access.release()

        return result

    @pulse_hold.setter
    def pulse_hold(self, value):
        self._mutex_dev_access.acquire()
        self._ch.pulse_hold = value
        self._mutex_dev_access.release()

    @property
    def period(self):
        self._mutex_dev_access.acquire()
        result = self._ch.pulse_period
        self._mutex_dev_access.release()

        return result

    @period.setter
    def period(self, value):
        self._mutex_dev_access.acquire()
        self._ch.pulse_period = value
        self._update_preview_variables()
        self._mutex_dev_access.release()

    @property
    def pulse_trans_lead(self):
        self._mutex_dev_access.acquire()
        result = self._ch.pulse_leading_transition
        self._mutex_dev_access.release()

        return result

    @pulse_trans_lead.setter
    def pulse_trans_lead(self, value):
        self._mutex_dev_access.acquire()
        self._ch.pulse_leading_transition = value
        self._mutex_dev_access.release()

    @property
    def pulse_trans_trail(self):
        self._mutex_dev_access.acquire()
        result = self._ch.pulse_trailing_transition
        self._mutex_dev_access.release()

        return result

    @pulse_trans_trail.setter
    def pulse_trans_trail(self, value):
        self._mutex_dev_access.acquire()
        self._ch.pulse_trailing_transition = value
        self._mutex_dev_access.release()
