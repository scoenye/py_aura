"""
    Aura USB
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
import hid

from abc import ABC
from udev import USBEventListener


class Device(ABC):
    """
    Base class for Aura USB devices
    """
    VENDOR_ID = 0x0b05
    PRODUCT_ID = 0x0000
    INTERFACE = 0

    def __init__(self):
        self.handle = None

    def _find_path(self):
        device_list = hid.enumerate(self.VENDOR_ID, self.PRODUCT_ID)

        for device in device_list:
            if device['interface_number'] == self.INTERFACE:
                return device['path']

    def open(self):
        """
        Ready the device for use
        :return:
        """
        path = self._find_path()

        try:
            self.handle = hid.Device(path=path)
        except Exception:
            raise ValueError('Device not found')

    def close(self):
        """
        Release the device
        :return:
        """
        self.handle.close()

    def write_interrupt(self, report):
        """
        Accept a report to send to the device's Aura endpoint
        :param report: report to send to the device
        :return: number of bytes transferred to the device
        """
        return report.send(self.handle)

    def read_interrupt(self, size, timeout=None):
        """
        Request a return report from the device's Aura endpoint
        :param size: amount of data requested
        :param timeout: milliseconds to wait before giving up
        :return: data transmitted by the device
        """
        return self.handle.read(size, timeout)


class GladiusIIMouse(Device):
    """
    Asus RoG Gladius II mouse
    """
    PRODUCT_ID = 0x1845
    INTERFACE = 2

    # Selectable LEDs
    LED_LOGO = 0x00     # Selects the logo LED
    LED_WHEEL = 0x01    # Selects the wheel LED
    LED_BASE = 0x02     # Selects the mouse base
    LED_ALL = 0x03      # Selects all LEDs


class ITEKeyboard(Device):
    """
    Asus ITE keyboard (8910)
    """
    PRODUCT_ID = 0x1869

    # Selectable segments
    LED_ALL = 0
    LED_SEGMENT1 = 1
    LED_SEGMENT2 = 2
    LED_SEGMENT3 = 3
    LED_SEGMENT4 = 4
    LED_SEGMENT5 = 5
    LED_SEGMENT6 = 6
    LED_SEGMENT7 = 7


# Supported devices
DEVICES = {
    '0b05': {
        '1845': GladiusIIMouse,
        '1869': ITEKeyboard
    }
}


class DeviceList(USBEventListener):
    """
    List of supported devices currently connected to the computer
    """
    def __init__(self):
        self.devices = {}

    def added(self, vendor_id, product_id, model):
        vendor_list = DEVICES.get(vendor_id)
        if vendor_list:
            if product_id in vendor_list:
                if vendor_id not in self.devices:
                    self.devices[vendor_id] = {}
                self.devices[vendor_id][product_id] = DEVICES[vendor_id][product_id]()

    def removed(self, vendor_id, product_id):
        print(vendor_id, product_id)

