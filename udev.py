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

from abc import ABC


class USBEventListener(ABC):
    """
    USBMonitor ebent listener interface
    """
    def added(self, vendor_id, product_id, model):
        """
        Signal a USB device was connected to the computer
        :param vendor_id: vendor ID of the device
        :param product_id: product ID of the device
        :param model: description of the device
        :return:
        """

    def removed(self, vendor_id, product_id):
        """
        Signal a USB device was disconnected from the computer
        :param vendor_id: vendor ID of the device
        :param product_id: product ID of the device
        :return:
        """


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
            self._send_add(device.properties.asint('ID_VENDOR_ID'),
                           device.properties.asint('ID_MODEL_ID'),
                           device.properties.asstring('ID_MODEL'))
        elif action == 'remove':
            self._send_remove(device.properties.asint('ID_VENDOR_ID'),
                              device.properties.asint('ID_MODEL_ID'))

    def _send_add(self, vendor_id, product_id, model):
        # Send 'add' signal to all listeners
        for listener in self.listeners:
            listener.added(vendor_id, product_id, model)

    def _send_remove(self, vendor_id, product_id):
        # Send 'remove' signal to all listeners
        for listener in self.listeners:
            listener.removed(vendor_id, product_id)

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
