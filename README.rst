Universal Signal Waveform Acquisition & Generation
==================================================

A *GUI*-based software for controlling oscilloscopes and signal
generators from a variety of vendors. Supported devices include:

- **Keysight Technologies** DSOX1102A
- **TiePie engineering** Handyscope HS3 & HS5
- **Tektronix** TBS1072C
- **Hantek** 6022BE/BL
- **Tektronix** AFG1022

Most prominent features are:

- Realtime display of oscilloscope measurement data (in both time and frequency
  domain)
- Preview of signal generator output according to the current settings
- *CSV* compatibility - load arbitrary data from file into signal generator &
  save displayed oscilloscope measurement data to file
- Hot plugging support - devices can be inserted or removed during runtime
- Runs on both *Linux* and *Windows*

.. image:: docs/images/osc_settings.gif
  :width: 90%
  :align: center
  :alt: Settings to control the oscilloscopes

Extending the software
----------------------

You can add more signal generators & oscilloscopes from other vendors to
the collection of compatible devices without much of a hassle by
following these 5 steps:

1. Have a look at what functionalities you need: ``gen_properties.py`` & ``osc_properties.py``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First determine, whether the device you want to add is of the type
*signal generator* (from now on abbreviated simply as *generator*) or
*oscilloscope*. Then, open the respective
``device_properties/...properties.py`` file. This file contains the
entire collection of methods and properties corresponding to that device
type across all vendors & models.

If the properties of the device you’re about to add happen to be a
subset of this collection, you can skip to **step 2**. Otherwise, you’ll
have to add new lines of code here.

You’ll notice that each device property requires implementation of two
*Python* functions. The first one always carries the ``@QtCore.Slot``
decorator, this is the function invoked by frontend. In order not to
block the *GUI* thread, this function will then invoke the second,
similarly named function in its own thread. Depending on the *value*
parameter passed by frontend, the ``..._thread`` function will then
access the getter and / or setter for that property.

You can use the existing functions as a template to implement the
missing ones. Just keep in mind that frontend **always** passes the
*value* parameter as *string*, so make sure to cast it properly before
use.

2. Implement the interface to the hardware: ``generators/`` & ``oscilloscopes/``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Have a look at the ``devices/device.py`` file and closely examine both
the classes (``Device`` & ``Channel``) featured in that file.
Afterwards, do the same with either ``devices/generator.py`` or
``devices/oscilloscope.py``, depending on the type of device you’re
about to add.

When you got a grasp of the concepts, create a new *Python* file for
your device in either the ``devices/generators/`` or the
``devices/oscilloscopes/`` subdirectory. In that file, create one class
that inherits from ``Generator`` or ``Oscilloscope``, respectively.
Then, add a second class that inherits from ``GenChannel`` or
``OscChannel``, respectively.

Both of the classes you’ve added in the newly created file must
implement all abstract methods, as well as the desired subset of getters
& setters invoked in the ``..._thread`` functions of
``device_properties/...properties.py``. You can use the existing
``...gen.py`` & ``...osc.py`` files as guidelines on how to use the
provided class variables, mutexes, methods, etc.

3. Enable the *Device Manager* to create objects of your new interface: ``device_manager.py``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In order to let the *Device Manager* create instances of the newly
implemented interface to your device, you’ll need to update
``device_manager.py``. In there, look for the ``_on_add_device`` method.

::

   ...
   elif device_vendor == 'Tiepie':
       added_devices.append(TiepieOsc(..., self._device_stopped))
       added_devices.append(TiepieGen(...))
   elif device_vendor == 'Keysight':
       added_devices.append(KeysightOsc(..., self._device_stopped))
   elif device_vendor == 'Tektronix':
       added_devices.append(TektronixGen(...))
   ...

Add another ``elif`` case for your device’s vendor where you append your
interface to ``added_devices``. Remember to pass
``self._device_stopped`` to your constructor if it’s an oscilloscope.

4. Make the *USB Daemon* recognize your device: ``usb_device_daemon.py``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The *USB Daemon* monitors the *USB* ports of the computer for events
caused by plugging devices in or out. If one of those devices happens to
be a generator or oscilloscope supported by the application, the
*Daemon* notifies the *Device Manager* which updates its device list
accordingly.

If your device isn’t an actual physical device that needs to be
connected via *USB*, you can skip to **step 5**. Otherwise, you’ll have
to add new lines of code in ``usb_device_daemon.py``.

Look for the ``_event_handler`` method.

::

   ...
   # get all available information on the device vendor
   ...

   # check which vendor's device was plugged in
   # and invoke "new device" callback function with corresponding parameters

   if 'TiePie engineering' in dev_vendor_info:

       ...

   elif 'Keysight_Technologies' in dev_vendor_info:

       ...

   elif 'TEKTRONIX' in dev_vendor_info:

       ...

   # for all VISA devices on Windows only
   elif 'IVI Foundation, Inc' in dev_vendor_info and platform == 'win32':
   ...

Add another ``elif`` case for your device’s vendor similar to the other
cases.

Remember to do these two updates within the case
``'IVI Foundation, Inc' in dev_vendor_info and platform == 'win32'`` if
your device uses the *VISA* interface, because it won’t be recognized on
*Windows* otherwise:

- Add the vendor’s name to the ``known_visa_vendors`` list
- Map the new entry in ``known_visa_vendors`` to the *Manufacturer ID* by extending
  the following snippet with another ``elif``:

::

   ...
   # prettify the list of all currently connected devices of this vendor
   ...
   for dev in dev_list_raw:

       ...
       if manufacturer == 'KEYSIGHT TECHNOLOGIES':
           visa_vendor = 'Keysight'
       elif manufacturer == 'TEKTRONIX':
           visa_vendor = 'Tektronix'
   ...

5. Design the *GUI*\ ’s settings bar for your device and its channels: ``qml/devices/generators/`` & ``qml/devices/oscilloscopes/``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When selecting an entry in the device list during application runtime,
frontend attempts to load two *QML* files, one for the overall device
settings and one for the channel-specific settings. These two files need
to be located inside of the ``qml/devices/generators/`` or
``qml/devices/oscilloscopes/`` directory, depending on the device type.
It is of great importance that the naming scheme for the files follows
this format, otherwise frontend won’t be able to find the correct file:

- ``Vendor_Modelname_DEVICE.qml`` for the device file
- ``Vendor_Modelname_CHANNEL.qml`` for the channel file

Create both files in the correct directory and then proceed to fill them
with appropriate content. You can use the existing files as templates in
order to do that. Basically you have to:

- Set the ``GridLayout``\ ’s number of columns to the number of available
  settings
- Create one text label for each setting describing what it does
- Create one widget (``ComboBox``, ``TextField``, ``CheckBox`` or ``Button``)
  for each setting which invokes the corresponding ``@QtCore.Slot`` function
  from ``device_properties/...properties.py``
- Adjust the ``reload...Settings`` function so that all property getters are
  called once. Remember that for comboboxes, you only need to call the
  ``..._avail`` function, since it will automatically invoke the getter for the
  current value
- Create one ``on...`` function for each value that is returned from backend
  after invoking property getters. Use the passed *value* parameter to update
  the corresponding widget’s current placeholder text, index selection, etc.

Summary
~~~~~~~

1. Check and potentially extend ``device_properties/...properties.py``
2. Create interface file in ``devices/.../`` with 2 classes inheriting
   from either ``Generator`` & ``GenChannel`` or ``Oscilloscope`` &
   ``OscChannel``.
3. Extend ``_on_add_device`` in ``device_manager.py``
4. Potentially extend ``_event_handler`` in ``usb_device_daemon.py``
5. Create ``Vendor_Modelname_DEVICE.qml`` &
   ``Vendor_Modelname_CHANNEL.qml`` in ``qml/devices/.../``
