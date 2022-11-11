import threading

from uniswag.devices.generators.tektronix_gen import TektronixGen
from uniswag.devices.generators.tiepie_gen import TiepieGen
from uniswag.devices.oscilloscopes.keysight_osc import KeysightOsc
from uniswag.devices.oscilloscopes.math_osc import MathOsc
from uniswag.devices.oscilloscopes.tiepie_osc import TiepieOsc
from uniswag.usb_device_daemon import USBDeviceDaemon


class DeviceManager:
    def __init__(self, list_event_callback, device_stopped_callback):
        """
        Provides an up-to-date list of currently accessible oscilloscopes and generators.

        Creates or deletes "Device" subclass objects and adds them to or removes them from the device list,
        depending on whether corresponding devices are connected or disconnected via USB
        (or added/removed by code in case of emulated devices).
        Device list updates are signaled by invoking the "list event" callback function.
        The "device stopped" callback function is simply forwarded to the device constructors and can be used to
        react to a device being stopped.

        Args:
            list_event_callback (function):
                The function to call when the device list has changed.
            device_stopped_callback (function):
                The function that is invoked by a device when it stops.

        Returns:
            DeviceManager:
                A DeviceManager object.
        """
        # a list containing all currently connected oscilloscope and generator devices
        self._device_list = []

        # a callback function that is invoked every time an entry is
        # added to or removed from the list of currently connected devices
        self._list_event = list_event_callback

        # a callback function that is passed to oscilloscopes;
        # it is invoked by the devices when they are stopped (manually or autonomously)
        self._device_stopped = device_stopped_callback

        # add the MathOsc to the device list
        add_math_osc = threading.Thread(target=
                                        lambda: self._on_add_device({'Name': 'MathOsc', 'SerNo': '123'}, 'MS-SWAG'),
                                        daemon=True)
        add_math_osc.start()

        # the USB device daemon monitors all USB ports and signals when
        # oscilloscopes or generators are inserted/removed
        self._usb_daemon = USBDeviceDaemon(self._on_add_device, self._on_remove_device)

    @property
    def device_list(self):
        """
        The list of currently connected oscilloscopes and generators.

        "Connected" can both mean plugged in via USB and emulated in software.

        Returns:
            list[uniswag.devices.device.Device]:
                An unsorted list containing the "Oscilloscope" and "Generator" objects.
        """
        return self._device_list

    def _on_add_device(self, device_id, device_vendor):
        """
        Adds one "Oscilloscope" and/or one "Generator" object associated with the specified vendor to the device list.

        After the device list is updated, the callback function to inform about the update is invoked.

        Args:
            device_id (dict[str, str]):
                The new device's name and serial number.
            device_vendor (str):
                The name of the new device's vendor.
        """
        # create new devices depending on the vendor
        added_devices = []
        if device_vendor == 'MS-SWAG':
            added_devices.append(MathOsc(device_id['Name'], device_id['SerNo'], self._device_stopped, self))
        elif device_vendor == 'Tiepie':
            added_devices.append(TiepieOsc(device_id['Name'], device_id['SerNo'], self._device_stopped))
            added_devices.append(TiepieGen(device_id['Name'], device_id['SerNo']))
        elif device_vendor == 'Keysight':
            added_devices.append(KeysightOsc(device_id['Name'], device_id['SerNo'], self._device_stopped))
        elif device_vendor == 'Tektronix':
            added_devices.append(TektronixGen(device_id['Name'], device_id['SerNo']))

        # add the new devices to the device list
        for dev in added_devices:
            self._device_list.append(dev)

        # invoke callback function to inform about the added devices
        self._list_event('add', added_devices)

    def _on_remove_device(self, device_id, device_vendor):
        """
        Removes one "Oscilloscope" and/or one "Generator" object associated with the specified vendor
        from the device list.

        After the device list is updated, the callback function to inform about the update is invoked.

        Args:
            device_id (dict[str, str]):
                The name and serial number of the device to remove.
            device_vendor (str):
                The vendor's name of the device to remove.
        """
        # find the oscilloscope and/or generator in the device list which is to be removed
        removed_devices = []
        for dev in self._device_list:
            if dev.id['Name'] == device_id['Name'] \
                    and dev.id['SerNo'] == device_id['SerNo'] \
                    and dev.id['Vendor'] == device_vendor:

                # disconnect device
                dev.init_deletion()
                removed_devices.append(dev)

        # remove the device(s)
        for dev in removed_devices:
            self._device_list.remove(dev)

        # invoke callback function to inform about the removed devices
        self._list_event('remove', removed_devices)
