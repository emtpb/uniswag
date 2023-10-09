from sys import platform

import tektronixosc

if platform == 'linux':
    import pyudev
elif platform == 'win32':
    import pyvisa as vi
    import wmi
    import pythoncom

import threading
import time
import queue
import handyscope
import keysightosc
import tektronixsg


class USBDeviceDaemon:
    def __init__(self, plug_in_event, plug_out_event):
        """
        Monitors USB ports for oscilloscopes and generators being plugged in and out.

        If a device from a known vendor is inserted/removed, the device's name and serial number are extracted and
        passed as parameters to the corresponding callback function.

        Args:
            plug_in_event (function):
                The function to call when a device from a known vendor has been plugged in to USB.
                Receives a shortened device ID as well as the vendor's name as parameters.
            plug_out_event (function):
                The function to call when a device from a known vendor has been plugged out from USB.
                Receives a shortened device ID as well as the vendor's name as parameters.

        Returns:
            USBDeviceDaemon:
                A USBDeviceDaemon object.
        """
        # the callback functions invoked when a known vendor's device is inserted/removed via USB
        self._add_event = plug_in_event
        self._remove_event = plug_out_event

        # a dict containing the shortened ID (= name and serial number), vendor and path of every
        # known and currently connected USB device (one list index for every device)
        self._usb_list = {'ShortID': [], 'Vendor': [], 'Path': []}

        # a queue for USB events
        # (event = what happened to which USB device)
        self._event_queue = queue.Queue()

        # a thread that continuously processes all events in the USB event queue
        self._event_handler_thread = threading.Thread(target=self._event_handler, daemon=True)
        self._event_handler_thread.start()

        if platform == 'linux':

            # initializes Linux USB library
            self._context = pyudev.Context()

            # enqueue all initially connected USB devices into the USB event queue
            all_connected_usb = self._context.list_devices(subsystem='usb')
            for device in all_connected_usb:
                if device.properties['DEVTYPE'] == 'usb_device':
                    self._event_queue.put(item=('bind',
                                                device.properties['DEVTYPE'],
                                                device.properties['DEVPATH'],
                                                device.properties),
                                          block=False)

            # start monitoring for USB events
            # (each event will invoke the specified callback function)
            self._monitor = pyudev.Monitor.from_netlink(self._context)
            self._monitor.filter_by(subsystem='usb')
            self._observer = pyudev.MonitorObserver(self._monitor, self._on_pyudev_event)
            self._observer.start()

        elif platform == 'win32':

            # initializes PyVISA for Windows
            self._busy_visa_resources = {}

            # initializes Windows USB library for the current thread
            pythoncom.CoInitialize()
            self._context = wmi.WMI()

            # enqueue all initially connected USB devices into the USB event queue
            all_connected_usb = self._context.query('Select * from Win32_USBControllerDevice')
            for device in all_connected_usb:
                device_type = device.Dependent.PNPClass
                if 'USB' in device_type:
                    device_path = device.Dependent.DeviceID
                    device_vendor = {'VENDOR': device.Dependent.Manufacturer}
                    self._event_queue.put(item=('bind', device_type, device_path, device_vendor), block=False)

            # start monitoring for USB events
            # (each thread will enqueue corresponding events into the USB event queue)
            self._observer = []
            self._observer.append(threading.Thread(target=self._on_wmi_usb_creation, daemon=True))
            self._observer.append(threading.Thread(target=self._on_wmi_usb_deletion, daemon=True))
            for thread in self._observer:
                thread.start()

    def _on_wmi_usb_creation(self):
        """
        Monitors the Windows USB controller for devices being plugged in and
        enqueues events into the USB event queue accordingly.

        Creates a tuple consisting of the event action ('bind'), the device type, the device path (alias ID) and
        the device vendor (wrapped in a dictionary).
        """
        # initializes Windows USB library for the current thread
        pythoncom.CoInitialize()
        context = wmi.WMI()

        # start monitoring for USB plug-in events
        monitor = context.Win32_USBControllerDevice.watch_for("creation")

        while True:
            # wait for a new creation issued by the Windows USB controller
            device = monitor()

            device_path = device.Dependent.split('DeviceID=')[1].split('"')[1].replace('\\\\', '\\')
            device_type = 'unknown'
            device_vendor = 'unknown'

            # get more info about the device that was just plugged in
            # by iterating through the list of all currently connected USB devices
            all_connected_devices = context.query('Select * from Win32_USBControllerDevice')
            for connected_device in all_connected_devices:
                if connected_device.Dependent.DeviceID == device_path:
                    device_type = connected_device.Dependent.PNPClass
                    device_vendor = {'VENDOR': connected_device.Dependent.Manufacturer}
                    break

            # enqueue an event into the USB event queue
            self._event_queue.put(item=('bind', device_type, device_path, device_vendor), block=False)

    def _on_wmi_usb_deletion(self):
        """
        Monitors the Windows USB controller for devices being plugged out and
        enqueues events into the USB event queue accordingly.

        Creates a tuple consisting of the event action ('unbind'), the device type ('usb_device'),
        the device path (alias ID) and an empty entry (None).
        """
        # initializes Windows USB library for the current thread
        pythoncom.CoInitialize()
        context = wmi.WMI()

        # start monitoring for USB plug-out events
        monitor = context.Win32_USBControllerDevice.watch_for("deletion")

        while True:
            # wait for a new deletion issued by the Windows USB controller
            device = monitor()

            device_path = device.Dependent.split('DeviceID=')[1].split('"')[1].replace('\\\\', '\\')

            # enqueue an event into the USB event queue
            self._event_queue.put(item=('unbind', 'usb_device', device_path, None), block=False)

    def _on_pyudev_event(self, action, device):
        """
        Enqueues an event into the USB event queue.

        Creates a tuple consisting of the event action, the device type, the device path and the entire device object.

        Args:
            action (str):
                The kind of event that occurred.
                Examples are "bind", "unbind", etc.
            device (pyudev.Device):
                The device object that the action was performed on.
                Provides several properties to access device information such as its vendor, USB path, etc.
        """
        self._event_queue.put(item=(action,
                                    device.properties['DEVTYPE'],
                                    device.properties['DEVPATH'],
                                    device.properties),
                              block=False)

    def _event_handler(self):
        """
        Continuously processes all events in the USB event queue.

        Depending on whether a device is added or removed, the corresponding callback function is invoked with
        the device ID and the vendor's name as parameters.
        All events are filtered by the following conditions:

        "bind" and "unbind" actions;
        "usb_device"/"USB" device types;
        vendors that are known
        """
        while True:
            # get the next event in the USB event queue
            item = self._event_queue.get()
            action = item[0]
            device_type = item[1]
            device_path = item[2]
            device_extras = item[3]

            # case: device plugged in
            if action == 'bind':

                # check for new usb devices
                if ((device_type == 'usb_device') or ('USB' in device_type)) \
                        and (device_path not in self._usb_list['Path']):

                    # get all available information on the device vendor
                    dev_vendor_info = []
                    for prop in device_extras:
                        if 'VENDOR' in prop:
                            dev_vendor_info.append(device_extras[prop])

                    # check which vendor's device was plugged in
                    # and invoke "new device" callback function with corresponding parameters

                    if 'TiePie engineering' in dev_vendor_info:

                        # get all the devices of this vendor that are already registered within the device list
                        registered_dev_list = self._devices_filtered_by_vendor('Tiepie')

                        # try to detect all currently connected devices of this vendor in a time frame of 10 seconds
                        dev_list_raw = self._get_non_formatted_device_list(
                            [handyscope.DeviceList().get_overview], registered_dev_list, 10)

                        # prettify the list of all currently connected devices of this vendor
                        dev_list_formatted = []
                        for dev in dev_list_raw:
                            short_id = {
                                'Name': dev['Name'],
                                'SerNo': str(dev['SerNo'])
                            }
                            dev_list_formatted.append(short_id)

                        # register the new device to the device list by comparing
                        # the list of all currently connected devices with the list of already registered devices
                        self._add_new_device(dev_list_formatted, registered_dev_list, 'Tiepie', device_path)

                    elif 'Keysight_Technologies' in dev_vendor_info:

                        # get all the devices of this vendor that are already registered within the device list
                        registered_dev_list = self._devices_filtered_by_vendor('Keysight')

                        # try to detect all currently connected devices of this vendor in a time frame of 10 seconds
                        dev_list_raw = self._get_non_formatted_device_list(
                            [keysightosc.list_connected_keysight_oscilloscopes], registered_dev_list, 10)

                        # prettify the list of all currently connected devices of this vendor
                        dev_list_formatted = []
                        for dev in dev_list_raw:
                            short_id = {
                                'Name': dev['Model'],
                                'SerNo': dev['Serial Number']
                            }
                            dev_list_formatted.append(short_id)

                        # register the new device to the device list by comparing
                        # the list of all currently connected devices with the list of already registered devices
                        self._add_new_device(dev_list_formatted, registered_dev_list, 'Keysight', device_path)

                    # Tektronix devices
                    elif '0699' in dev_vendor_info:

                        # get all the devices of this vendor that are already registered within the device list
                        registered_dev_list = self._devices_filtered_by_vendor('Tektronix')

                        # try to detect all currently connected devices of this vendor in a time frame of 10 seconds
                        dev_list_raw = self._get_non_formatted_device_list(
                            [tektronixsg.list_connected_tektronix_generators,
                             tektronixosc.list_connected_tektronix_oscilloscopes], registered_dev_list, 10)

                        # prettify the list of all currently connected devices of this vendor
                        dev_list_formatted = []
                        for dev in dev_list_raw:
                            short_id = {
                                'Name': dev['Model'],
                                'SerNo': dev['Serial Number'],
                                'Type': 'OSC' if 'TBS' in dev['Model'] else 'GEN'
                            }
                            dev_list_formatted.append(short_id)

                        # register the new device to the device list by comparing
                        # the list of all currently connected devices with the list of already registered devices
                        self._add_new_device(dev_list_formatted, registered_dev_list, 'Tektronix', device_path)

                    # for all VISA devices on Windows only
                    elif 'IVI Foundation, Inc' in dev_vendor_info and platform == 'win32':

                        # get all the devices of this vendor that are already registered within the device list
                        known_visa_vendors = ['Keysight', 'Tektronix']
                        registered_dev_list = []
                        for vendor in known_visa_vendors:
                            registered_dev_list += self._devices_filtered_by_vendor(vendor)

                        # try to detect all currently connected devices of this vendor in a time frame of 10 seconds
                        dev_list_raw = self._get_non_formatted_device_list(
                            self._list_connected_visa_devices, registered_dev_list, 10)

                        # prettify the list of all currently connected devices of this vendor
                        dev_list_formatted = []
                        for dev in dev_list_raw:

                            visa_vendor = 'unknown'
                            manufacturer = dev['Manufacturer']
                            if manufacturer == 'KEYSIGHT TECHNOLOGIES':
                                visa_vendor = 'Keysight'
                            elif manufacturer == 'TEKTRONIX':
                                visa_vendor = 'Tektronix'

                            visa_id = {
                                'Vendor': visa_vendor,
                                'Name': dev['Model'],
                                'SerNo': dev['Serial Number']
                            }
                            dev_list_formatted.append(visa_id)

                        # register the new device to the device list by comparing
                        # the list of all currently connected devices with the list of already registered devices
                        self._add_new_device(dev_list_formatted, registered_dev_list, None, device_path)

            # case: formerly plugged in device removed
            elif action == 'unbind':

                # check for known usb devices
                if (device_type == 'usb_device') \
                        and (device_path in self._usb_list['Path']):

                    # get the removed device's list index
                    idx = self._usb_list['Path'].index(device_path)

                    # get the removed device's name, serial number and vendor
                    removed_device = self._usb_list['ShortID'][idx], self._usb_list['Vendor'][idx]

                    # remove the device from the list of currently registered devices
                    del self._usb_list['ShortID'][idx]
                    del self._usb_list['Vendor'][idx]
                    del self._usb_list['Path'][idx]

                    # invoke "device removed" callback function
                    self._remove_event(*removed_device)

            # event in the USB event queue successfully processed
            self._event_queue.task_done()

    def _devices_filtered_by_vendor(self, vendor):
        """
        Compiles a list of the currently registered devices filtered by the given vendor name.

        The currently registered devices are a subset of the currently connected USB devices.
        A device might be connected via USB, but not yet registered within the list.

        Args:
            vendor (str):
                The name of the vendor by which to filter the resulting list.

        Returns:
            list[dict[str, str]]:
                The list of the given vendor's currently registered USB devices.
                Each device is represented by its shortened ID (name and serial number).
        """
        filter_result = []

        # find all occurrences of the specified vendor in the list of currently registered devices
        for i in range(len(self._usb_list['Vendor'])):
            if self._usb_list['Vendor'][i] == vendor:
                filter_result.append(self._usb_list['ShortID'][i])

        return filter_result

    def _add_new_device(self, all_devices, registered_devices, vendor, path):
        """
        Compares both the "all devices" and "registered devices" lists and
        registers the first device from the first list that is not yet in the second.

        Afterwards, the "new device" callback function is invoked with
        the shortened device ID (name and serial number) and the vendor's name.

        Args:
            all_devices (list[dict[str, str]]):
                All the devices from a single vendor that are currently connected via USB.
            registered_devices (list[dict[str, str]]):
                Only the already registered devices from the same vendor* that are currently connected via USB.
                Subset of the first list.
                (*If the vendor parameter is None, both lists may also contain devices from different vendors.)
            vendor (str or None):
                The name of the vendor to which the devices in both lists belong.
                If this is None, the "all devices" list is required to provide the vendor for each entry instead.
            path (str):
                The USB path of the newly registered device.
                This should simply be the USB path of the device that was just plugged in.
        """
        # check for every connected USB device if it is already in the list of registered devices
        for plugged_in_device in all_devices:
            new_device = True
            for reg_dev in registered_devices:
                if plugged_in_device['Name'] == reg_dev['Name'] and plugged_in_device['SerNo'] == reg_dev['SerNo']:
                    new_device = False
                    break

            # register the device if it could not be found in the list of registered devices
            if new_device:

                if vendor is not None:
                    device_vendor = vendor
                else:
                    device_vendor = plugged_in_device['Vendor']

                short_id = {
                    'Name': plugged_in_device['Name'],
                    'SerNo': plugged_in_device['SerNo'],
                    'Type': plugged_in_device['Type']
                }
                self._usb_list['ShortID'].append(short_id)
                self._usb_list['Vendor'].append(device_vendor)
                self._usb_list['Path'].append(path)

                # invoke "new device" callback function
                self._add_event(short_id, device_vendor)

                break

    @staticmethod
    def _get_non_formatted_device_list(library_functions_for_getting_devices, registered_devices, timeout):
        """
        Invokes the passed callback function to obtain the library-specific list of currently connected devices.

        Args:
            library_functions_for_getting_devices (list(function)):
                The callback functions which return the list of currently connected devices from the desired vendor.
            registered_devices (list[dict[str, str]]):
                Used for reference to determine, if the obtained library-specific device list is complete.
                There should be at least one more device connected via USB than currently registered.
            timeout (float):
                The timeout for this method in seconds.
                If reached, an error message is printed to console.

        Returns:
            list:
                The return value of the library function call.
        """
        connected_devices_raw = []

        # set timeout in seconds
        latest_point_in_time = time.time() + timeout

        # there should be at least one more device connected via USB than currently registered
        while not len(connected_devices_raw) > len(registered_devices):

            time.sleep(0.5)
            try:
                for function in library_functions_for_getting_devices:
                    # invoke callback function to obtain the library-specific device list
                    connected_devices_raw += function()

            except OSError as e:
                # reset library-specific device list if encountering an error
                print(e)
                connected_devices_raw = []

            # abort on timeout
            if time.time() > latest_point_in_time:
                print("A problem occurred while trying to detect the inserted device.")
                break

        return connected_devices_raw

    def _list_connected_visa_devices(self):
        """
        The list of all currently connected PyVISA devices (Windows only).

        This function is designed to obtain a list of VISA devices on Windows,
        since the OS is unable to differentiate between different VISA device vendors (unlike Linux).

        Returns:
            list[dict[str, str]]:
                A list containing information about every connected PyVISA device.
                Each entry consists of a dictionary with the keys "Manufacturer", "Model" & "Serial Number".
        """
        rm = vi.ResourceManager()

        # list of all connected VISA device addresses
        resource_list = rm.list_resources()

        # delete devices from the dictionary of busy VISA resources that have already been unplugged
        keys_to_delete = []
        for key in self._busy_visa_resources:
            if key not in resource_list:
                keys_to_delete.append(key)
        for key in keys_to_delete:
            self._busy_visa_resources.pop(key, None)

        # compile a list containing manufacturer name, model descriptor and serial number of each connected VISA device
        device_list = []
        for res_num in range(len(resource_list)):

            res_parts = resource_list[res_num].split('::')
            if len(res_parts) > 3 and 'USB' in res_parts[0]:
                resource = resource_list[res_num]

                # get the Identification Number of the resource
                try:
                    if resource not in self._busy_visa_resources:
                        visa_device = rm.open_resource(resource)
                        idn = visa_device.query('*IDN?')
                        idn_parts = idn.split(',')
                        resource_info = {
                            'Manufacturer': idn_parts[0],
                            'Model': idn_parts[1],
                            'Serial Number': idn_parts[2]
                        }
                        self._busy_visa_resources[resource] = resource_info
                        device = resource_info
                    else:
                        device = self._busy_visa_resources[resource]
                except (vi.errors.VisaIOError, ValueError):
                    device = None

                if device is not None:
                    device_list.append(device)

        return device_list
