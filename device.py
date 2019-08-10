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

from report import GladiusIIReport, ITEKeyboardReport, ITEFlushReport


class Device:
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
        Transmit the report to the device's Aura endpoint
        :param report: data to send to the device
        :return: number of bytes transferred to the device
        """
        c_report = (ctypes.c_char * 64).from_buffer(report)

        return self.handle.write(c_report)

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
    LED_BASE = 0x02     # Selects the mouse base LED

    def __init__(self):
        super().__init__()
        self.report = GladiusIIReport()
        # Mouse needs all component LEDs targeted before it will acknowledge
        # requests to change individual LEDs.
        self.initialised = False

    def _change_color(self, red, green, blue, targets):
        # Execute the actual color change
        self.report.color(red, green, blue)

        for target in targets:
            self.report.target(target)
            xferred = self.report.send(self)
            print('write M0: ', xferred)

    def set_color(self, red, green, blue, targets=None):
        """
        Set one or more LEDs to the specified color.
        :param red: Red value, 0 - 255
        :param green: Green value, 0 - 255
        :param blue: Blue value, 0 - 255
        :param targets: list of LEDs to change color of, None to change all LEDs
        :return:
        """
        if not self.initialised or targets is None:
            targets = [GladiusIIMouse.LED_LOGO, GladiusIIMouse.LED_WHEEL, GladiusIIMouse.LED_BASE]
            if not self.initialised:
                self._change_color(0x00, 0x00, 0x00, targets)
                self.initialised = True

        self._change_color(red, green, blue, targets)


class ITEKeyboard(Device):
    """
    Asus ITE keyboard (8910)
    """
    PRODUCT_ID = 0x1869

    def __init__(self):
        super().__init__()
        self.color_report = ITEKeyboardReport()
        self.flush_report = ITEFlushReport()

    def set_color(self, red, green, blue, targets=None):
        """
        Change to a static color
        :param red: Red value, 0 - 255
        :param green: Green value, 0 - 255
        :param blue: Blue value, 0 - 255
        :param targets: Unused for the keyboard
        :return:
        """
        # Keyboard is complicated - this to change all segments at once
        # - Send color report (64 b)
        # - Send color report (64 b)
        # - Send color report with 0xe1 in byte 7 (64 b)
        # - Send "flush" report (64 b, 2nd byte 0xb5)
        self.color_report.color(red, green, blue)

        xferred = self.color_report.send(self)
        print('write K0: ', xferred)

        xferred = self.color_report.send(self)
        print('write K1: ', xferred)

        self.color_report.byte_7_e1()
        xferred = self.color_report.send(self)
        print('write K3: ', xferred)

        xferred = self.flush_report.send(self)
        print('write K4: ', xferred)
