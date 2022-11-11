import threading


class Device:
    def __init__(self, vendor, name, ser_no, dev_type):
        """
        Base class for all oscilloscopes and signal generators.

        Each device can be identified by its unique ID consisting of four parts ('Vendor', 'Name', 'SerNo', 'DevType').
        Furthermore, each device possesses a list of Channel (sub-)class objects,
        an attribute indicating whether it is currently running or halted
        and methods to start & stop the device.
        Also, there exists a kind of destructor which allows for clean deletion of Device objects.

        Args:
            vendor (str):
                The name of the device's vendor.
                Used for the 'Vendor' part of the device's ID.
            name (str):
                The moniker of the device.
                Used for the 'Name' part of the device's ID.
            ser_no (str):
                The serial number of the device.
                Used for the 'SerNo' part of the device's ID.
            dev_type (str):
                The type of device.
                'Osc' for oscilloscopes and 'Gen' for signal generators.
        Returns:
            Device:
                A Device object.
        """
        # the complete device ID, different for every single Device (sub-)class object
        self._id = {'Vendor': vendor, 'Name': name, 'SerNo': ser_no, 'DevType': dev_type}

        # the list of Channel (sub-)class objects belonging to the device
        self._ch = []

        # a threading lock which ensures that only one device (channel) property is read/changed at a time
        self._mutex_dev_access = threading.Lock()

    @property
    def id(self):
        """
        The device's ID.

        It contains the device's vendor, name, serial number and type ('Osc' or 'Gen').

        Returns:
            dict[str, str]:
                A dictionary with the keys 'Vendor', 'Name', 'SerNo' and 'DevType'.
        """
        return self._id

    @property
    def ch_cnt(self):
        """
        The number of channels that the device has.

        Returns:
            int:
                The length of the device's channel list.
        """
        return len(self._ch)

    @property
    def ch(self):
        """
        The list of all the device's channels.

        Returns:
            list[Channel]:
                The list of Channel (sub-)class objects belonging to the device.
        """
        return self._ch

    # ABSTRACT METHODS #################################################################################################

    def init_deletion(self):
        """
        A kind of "pseudo-destructor".

        This method is called right before the Device object is deleted
        (due to being removed from the computer).
        """
        raise NotImplementedError

    @property
    def is_running(self):
        """
        Indicates, whether the device is currently running or halted.

        Returns:
            bool:
                True if the device is running, False otherwise.
        """
        raise NotImplementedError

    def start(self):
        """
        Start the device.

        Will make an oscilloscope start its measurement and a generator begin to output its signal.
        As a result, the device will now be considered "running" until certain conditions are met.

        Returns:
            bool:
                True if the device was successfully started, False otherwise.
        """
        raise NotImplementedError

    def stop(self):
        """
        Stop the device.

        Will make an oscilloscope stop measuring and a generator disable the signal output.
        As a result, the device will now be considered "halted" until restarted.

        Returns:
            bool:
                True if the device was successfully stopped, False otherwise.
        """
        raise NotImplementedError


class Channel:
    def __init__(self, name, ch_no, mutex):
        """
        Base class for all device channels.

        Each channel can be identified by its ID, which is unique within the scope of the associated device.
        The ID consists of two parts ('Name', 'No').
        Furthermore, each channel possesses an attribute to enable or disable its input/output
        as well as a mutex for thread-safe access to the corresponding device.

        Args:
            name (str):
                The moniker of the channel.
                Used for the 'Name' part of the channel's ID.
            ch_no (int):
                The number of the channel.
                Used for the 'No' part of the channel's ID.
            mutex (threading.Lock):
                The same threading lock that is used for every other property access to the associated device.

        Returns:
            Channel:
                A Channel object.
        """
        # the complete channel ID,
        # only different for every Channel (sub-)class object in regard of the associated device (!)
        self._id = {'Name': name, 'No': ch_no}

        # a threading lock which ensures that only one device (channel) property is read/changed at a time
        self._mutex_dev_access = mutex

        # indicates, whether the channel input/output is currently enabled
        self._is_enabled = False

    @property
    def id(self):
        """
        The channel's ID.

        It contains the channel's name and number (counting starts from 1, not 0).

        Returns:
            dict[str, Any]:
                A dictionary with the keys 'Name' and 'No'.
        """
        return self._id

    @property
    def is_enabled(self):
        """
        Indicates, whether the channel input/output is currently enabled.

        Returns:
            bool:
                True if the channel is enabled, False otherwise.
        """
        return self._is_enabled

    # ABSTRACT METHODS #################################################################################################

    @is_enabled.setter
    def is_enabled(self, value):
        """
        Enables or disables the channel input/output.

        Args:
            value (bool):
                True to enable the channel, False to disable it.
        """
        raise NotImplementedError
