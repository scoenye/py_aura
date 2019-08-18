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
import ctypes
import hid

from abc import ABC, abstractmethod
from report import GladiusIIReport, ITEKeyboardReport, ITEFlushReport, ITEKeyboardSegmentReport


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

    @abstractmethod
    def change_color(self):
        """
        Execute the staged color change report.
        :return:
        """

    @abstractmethod
    def stage_color(self, red, green, blue, targets=None):
        """
        Prepare a color change for a set of LEDs. This method can be called several times to build a single report.
        Later calls will overwrite earlier changes where the target elements overlap.
        :param red: Red value, 0 - 255
        :param green: Green value, 0 - 255
        :param blue: Blue value, 0 - 255
        :param targets: list of LEDs or segments to change the color of, None to change all LEDs/segments
        :return:
        """

    @abstractmethod
    def set_color(self, red, green, blue):
        """
        Set all LEDs/segments to the specified color immediately
        :param red: Red value, 0 - 255
        :param green: Green value, 0 - 255
        :param blue: Blue value, 0 - 255
        :return:
        """


class GladiusIIMouse(Device):
    """
    Asus RoG Gladius II mouse
    """
    PRODUCT_ID = 0x1845
    INTERFACE = 2

    # Selectable LEDs
    LED_LOGO = 0x00     # Selects the logo LED
    LED_WHEEL = 0x01    # Selects the wheel LED
    LED_BASE = 0x02     # Selects the mouse base LED

    # The mouse does not appear to have a parallel report like ITEKeyboardSegmentReport. To make both devices look the
    # same to clients, the parallel report is simulated by the stage_color and change_color methods in combination.

    def __init__(self):
        super().__init__()
        self.report = GladiusIIReport()
        self.targets = []

    def change_color(self):
        """
        Execute the color change
        :return:
        """
        for target in self.targets:
            self.report.target(target)
            xferred = self.report.send(self)
            print('write M0: ', xferred)

    def stage_color(self, red, green, blue, targets=None):
        """
        Prepare a color change for a set of LEDs
        :param red: Red value, 0 - 255
        :param green: Green value, 0 - 255
        :param blue: Blue value, 0 - 255
        :param targets: list of LEDs to change color of, None to change all segments
        :return:
        """
        self.report.color(red, green, blue)
        if targets is None:
            self.targets = [GladiusIIMouse.LED_LOGO, GladiusIIMouse.LED_WHEEL, GladiusIIMouse.LED_BASE]
        else:
            self.targets = targets

    def set_color(self, red, green, blue):
        """
        Set all LEDs to the specified color immediately
        :param red: Red value, 0 - 255
        :param green: Green value, 0 - 255
        :param blue: Blue value, 0 - 255
        :return:
        """
        self.stage_color(red, green, blue)
        self.change_color()


class ITEKeyboard(Device):
    """
    Asus ITE keyboard (8910)
    """
    PRODUCT_ID = 0x1869

    # Selectable segments - value is the offset of the red byte
    LED_SEGMENT1 = 0
    LED_SEGMENT2 = 1
    LED_SEGMENT3 = 2
    LED_SEGMENT4 = 3
    LED_SEGMENT5 = 4
    LED_SEGMENT6 = 5
    LED_SEGMENT7 = 6

    def __init__(self):
        super().__init__()
        self.color_report = ITEKeyboardReport()
        self.segmented_report = ITEKeyboardSegmentReport()
        self.flush_report = ITEFlushReport()

    def change_color(self):
        """
        Execute the color change
        :return:
        """
        xferred = self.segmented_report.send(self)
        print('write K: ', xferred)

    def stage_color(self, red, green, blue, targets=None):
        """
        Prepare a color change for a set of segments
        :param red: Red value, 0 - 255
        :param green: Green value, 0 - 255
        :param blue: Blue value, 0 - 255
        :param targets: list of segments to change color of, None to change all segments
        :return:
        """
        if targets is None:
            targets = [ITEKeyboard.LED_SEGMENT1, ITEKeyboard.LED_SEGMENT2, ITEKeyboard.LED_SEGMENT3,
                       ITEKeyboard.LED_SEGMENT4, ITEKeyboard.LED_SEGMENT5, ITEKeyboard.LED_SEGMENT6,
                       ITEKeyboard.LED_SEGMENT7]

        self.segmented_report.color(red, green, blue, targets)

    def set_color(self, red, green, blue):
        """
        Change all segments to a single color immediately
        :param red:
        :param green:
        :param blue:
        :return:
        """
        # This uses ITEKeyboardReport to change the color of all segments at once.
        self.color_report.color(red, green, blue)

        xferred = self.color_report.send(self)
        print('write K0: ', xferred)

        xferred = self.color_report.send(self)
        print('write K1: ', xferred)

        xferred = self.flush_report.send(self)  # Additional observation in strobe effect
        print('write K4: ', xferred)

        self.color_report.byte_7_e1()
        xferred = self.color_report.send(self)
        print('write K3: ', xferred)

        xferred = self.flush_report.send(self)
        print('write K4: ', xferred)
