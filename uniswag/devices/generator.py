import threading

import numpy as np
import scipy.signal

from uniswag.devices.device import Device, Channel


class Generator(Device):
    def __init__(self, vendor, name, ser_no):
        """
        Base class for all signal generators, inherits from Device.

        Args:
            vendor (str):
                The name of the generator's vendor.
                Used for the 'Vendor' part of the device's ID.
            name (str):
                The moniker of the generator.
                Used for the 'Name' part of the device's ID.
            ser_no (str):
                The serial number of the generator.
                Used for the 'SerNo' part of the device's ID.

        Returns:
            Generator:
                A Generator object.
        """
        super().__init__(vendor, name, ser_no, 'Gen')

    def init_deletion(self):
        self._term_deletion()

    # ABSTRACT METHODS #################################################################################################

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


class GenChannel(Channel):
    def __init__(self, name, ch_no, mutex):
        """
        Base class for all generator channels, inherits from Channel.

        Args:
            name (str):
                The moniker of the generator channel.
                Used for the 'Name' part of the channel's ID.
            ch_no (int):
                The number of the generator channel.
                Used for the 'No' part of the channel's ID.
            mutex (threading.Lock):
                The same threading lock that is used for every other property access to the associated device.

        Returns:
            GenChannel:
                A GenChannel object.
        """
        super().__init__(name, ch_no, mutex)

        # the number of data points in the signal preview graph
        self._preview_samples = 1000

        # locally stored attributes based on signal generator properties, influence the signal preview graph
        self._signal_type = 'unknown'
        self._amplitude = 1
        self._offset = 1
        self._period = 1
        self._phase = 1
        self._symmetry = 1
        self._duty_cycle = 1
        self._arbitrary_data = [[0], [0]]

        # prevents the variables that influence the shape of the signal preview graph
        # from being accessed by multiple threads concurrently
        self._mutex_preview_variables = threading.Lock()

    def get_signal_preview(self):
        """
        The data that depicts the waveform of the channel's currently generated signal.

        It is split into the resulting X and Y vector.

        Returns:
            (np.ndarray, np.ndarray):
                A tuple containing the vector of the time values and the voltage values, respectively.
        """
        self._mutex_preview_variables.acquire()

        if self._signal_type == 'sine':
            time_vector = np.linspace(0, self._period, self._preview_samples)
            voltage_vector = self._amplitude * np.sin(
                (2 * np.pi / self._period) * (time_vector + (self._phase / 360) * self._period)) + self._offset

        elif self._signal_type == 'square':
            time_vector = np.linspace(0, self._period, self._preview_samples, endpoint=False)
            voltage_vector = self._amplitude * scipy.signal.square(
                (2 * np.pi / self._period) * (time_vector + (self._phase / 360) * self._period)) + self._offset

        elif self._signal_type == 'ramp':
            start_phase = 180 * self._symmetry + self._phase
            time_vector = np.linspace(0, self._period, self._preview_samples, endpoint=False)
            voltage_vector = self._amplitude * scipy.signal.sawtooth(
                2 * np.pi / self._period * (time_vector + (start_phase / 360) * self._period),
                width=self._symmetry) + self._offset

        elif self._signal_type == 'pulse':
            time_vector = np.linspace(0, self._period, self._preview_samples, endpoint=False)
            voltage_vector = self._amplitude * scipy.signal.square(
                (2 * np.pi / self._period) * (time_vector + (self._phase / 360) * self._period),
                duty=self._duty_cycle) + self._offset

        elif self._signal_type == 'arbitrary':
            time_vector = np.array(self._arbitrary_data[0])
            voltage_vector = np.array(self._arbitrary_data[1])

        else:
            time_vector = np.array([0.0])
            voltage_vector = np.array([0.0])

        self._mutex_preview_variables.release()

        return time_vector, voltage_vector

    # ABSTRACT METHODS #################################################################################################

    def _update_preview_variables(self):
        """
        Updates the values of all variables that influence the shape of the signal preview graph.

        Reads several of the currently set device settings in order to convert those values for the attributes
        "signal type", "amplitude", "offset", "period", "phase", "symmetry", "duty cycle" and "arbitrary data".
        """
        raise NotImplementedError

    @Channel.is_enabled.setter
    def is_enabled(self, value):
        raise NotImplementedError
