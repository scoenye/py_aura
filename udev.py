"""
    Nimbus USB
    A tool to change the LED colors on Asus USB HID peripherals

    Copyright (C) 2019  Sven Coenye

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or any
    later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import pyudev

from abc import ABC, abstractmethod


class USBEventListener(ABC):
    """
    USBMonitor event listener interface
    """
    @abstractmethod
    def added(self, vendor_id, product_id, bus_num, dev_num, model):
        """
        Signal a USB device was connected to the computer. The USB bus and device numbers are included to disambiguate
        multiple devices with the same vendor/device IDs.
        :param vendor_id: vendor ID of the device
        :param product_id: product ID of the device
        :param bus_num: USB bus the device is connected to
        :param dev_num: Device numnber on the USB bus
        :param model: description of the device
        :return:
        """

    @abstractmethod
    def removed(self, bus_num, dev_num):
        """
        Signal a USB device was disconnected from the computer. The USB bus and device numbers are included to
        disambiguate multiple devices with the same vendor/device IDs.
        :param bus_num: USB bus the device is connected to
        :param dev_num: Device numnber on the USB bus
        :return:
        """


class USBEnumerator:
    """
    Report the currently plugged in USB devices
    """
    def __init__(self):
        self.context = pyudev.Context()
        self.listeners = set()

    def enumerate(self):
        devices = pyudev.Enumerator(self.context).match_subsystem(subsystem='usb') \
                                                 .match_property('DEVTYPE', 'usb_device')
        for device in devices:
            self._send_add(device.properties['ID_VENDOR_ID'],
                           device.properties['ID_MODEL_ID'],
                           device.properties.asint('BUSNUM'),
                           device.properties.asint('DEVNUM'),
                           device.properties['ID_MODEL'])

    def _send_add(self, vendor_id, product_id, bus_num, dev_num, model):
        # Send 'add' signal to all listeners
        for listener in self.listeners:
            listener.added(vendor_id, product_id, bus_num, dev_num, model)

    def add_listener(self, listener):
        """
        Add a listener to the collection who will be notified when a USB event occurs.
        :param listener: listener instance to add to the collection
        :return:
        """
        self.listeners.add(listener)

    def remove_listener(self, listener):
        """
        Remove a listener to the collection who will be notified when a USB event occurs.
        :param listener: listener instance to remove from the collection
        :return:
        """
        if listener in self.listeners:
            self.listeners.remove(listener)


class USBMonitor:
    """
    Monitor udev for detection of USB events
    """
    def __init__(self):
        """ Initiate the object """
        self.context = pyudev.Context()
        monitor = pyudev.Monitor.from_netlink(self.context)
        # device_type should filter out interfaces
        monitor.filter_by(subsystem='usb', device_type='usb_device')
        # Not using the Qt binding as there is no reason to tie this to the GUI.
        self.observer = pyudev.MonitorObserver(monitor, self._handler)
        self.listeners = set()

    def _handler(self, action, device):
        """
        Callback for the pyudev observer
        :param action: device action detected by udev
        :param device: pyudev Device instance
        :return:
        """
        # Reported actions for the mouse are 'add', 'bind', 'remove' and 'unbind'. Pass 'add' and 'remove'
        # to the listeners. Translate the sysfs path here to vendor/device IDs and pass those on. That way,
        # there are no pyudev dependencies outside this module. Events are triggered for each interface on
        # a USB device. Pass them all on so we don't need to remember anything here.
        if action == 'add':
            self._send_add(device.properties['ID_VENDOR_ID'],
                           device.properties['ID_MODEL_ID'],
                           device.properties.asint('BUSNUM'),
                           device.properties.asint('DEVNUM'),
                           device.properties['ID_MODEL'])
        elif action == 'remove':
            self._send_remove(device.properties.asint('BUSNUM'),
                              device.properties.asint('DEVNUM'))

    def _send_add(self, vendor_id, product_id, bus_num, dev_num, model):
        # Send 'add' signal to all listeners
        for listener in self.listeners:
            listener.added(vendor_id, product_id, bus_num, dev_num, model)

    def _send_remove(self, bus_num, dev_num):
        # Send 'remove' signal to all listeners
        for listener in self.listeners:
            listener.removed(bus_num, dev_num)

    def start(self):
        """
        Start USB monitoring thread
        :return:
        """
        self.observer.start()

    def stop(self):
        """
        Signal the thread to stop running.
        :return:
        """
        self.observer.stop()

    def add_listener(self, listener):
        """
        Add a listener to the collection who will be notified when a USB event occurs.
        :param listener: listener instance to add to the collection
        :return:
        """
        self.listeners.add(listener)

    def remove_listener(self, listener):
        """
        Remove a listener to the collection who will be notified when a USB event occurs.
        :param listener: listener instance to remove from the collection
        :return:
        """
        if listener in self.listeners:
            self.listeners.remove(listener)


class NodeResolver:
    """
    The only attribute in common between the hid and pyudev modules is the device serial number, which is
    not reliably present on hardware. This class serves to link both and maintain the ability to distinguish
    multiple identical devices.
    """
    @staticmethod
    def bus_location(device_node):
        """
        Return the USB bus and device numbers corresponding to a device node. If the device node does not have its
        own bus & device numbers, the device chain is climbed until the first parent is found which does.
        :param device_node: device node path
        :return: (bus number, device number); None if no device in the chain has a bus & device number.
        """
        context = pyudev.Context()
        device = pyudev.Devices.from_device_file(context, device_node)

        while device:
            if device.properties.get('BUSNUM'):
                return device.properties.asint('BUSNUM'), device.properties.asint('DEVNUM')
            else:
                device = device.parent

        return None
