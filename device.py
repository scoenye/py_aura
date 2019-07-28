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

from report import GladiusIIReport, ITEKeyboardReport


class Device:
    """
    Base class for Aura USB devices
    """
    VENDOR_ID = 0x0b05
    PRODUCT_ID = 0x0000

    def __init__(self):
        self.handle = None
        self.aura_interface = 0
        self.kernel_attached = False
        self.endpoint_out = 0x00        # Override in subclass
        self.endpoint_in = 0x00         # Override in subclass

    def open(self, usb_context):
        """
        Ready the device for use
        :param usb_context:
        :return:
        """
        self.handle = usb_context.openByVendorIDAndProductID(
            self.VENDOR_ID,
            self.PRODUCT_ID,
            skip_on_error=True,
        )

        if self.handle is None:
            raise ValueError('Device not found')

        self.kernel_attached = self.handle.kernelDriverActive(self.aura_interface)
        if self.kernel_attached:
            self.handle.detachKernelDriver(self.aura_interface)

        self.handle.claimInterface(self.aura_interface)

    def close(self):
        """
        Release the device
        :return:
        """
        self.handle.releaseInterface(self.aura_interface)
        if self.kernel_attached:
            self.handle.attachKernelDriver(self.aura_interface)

        self.handle.close()

    def write_interrupt(self, report, size):
        """
        Transmit the report to the device's interrupt endpoint
        :param size: length of the block of data to send
        :param report: data to send to the device
        :return:
        """
        return self.handle.interruptWrite(self.endpoint_out, report, size)


class GladiusIIMouse(Device):
    """
    Asus RoG Gladius II mouse
    """
    PRODUCT_ID = 0x1845

    # Selectable LEDs
    LED_LOGO = 0x00     # Selects the logo LED
    LED_WHEEL = 0x01    # Selects the wheel LED
    LED_BASE = 0x02     # Selects the mouse base LED

    def __init__(self):
        super().__init__()
        self.aura_interface = 2
        self.report = GladiusIIReport()
        self.endpoint_out = 0x04
        self.endpoint_in = 0x83

    def static_color(self, red, green, blue, targets=None):
        """
        Change to a static color
        :param red: Red value, 0 - 255
        :param green: Green value, 0 - 255
        :param blue: Blue value, 0 - 255
        :param targets: list of LEDs to change color of, None to change all LEDs
        :return:
        """
        if targets is None:
            targets = [GladiusIIMouse.LED_LOGO, GladiusIIMouse.LED_WHEEL, GladiusIIMouse.LED_BASE]

        self.report.color(red, green, blue)

        for target in targets:
            self.report.target(target)
            xferred = self.report.send(self)
            print('write M0: ', xferred)


class ITEKeyboard(Device):
    """
    Asus ITE keyboard (8910)
    """
    PRODUCT_ID = 0x1869

    # Keyboard is complicated
    # - may need SET_IDLE call
    # - Send color report (64 b)
    # - Send 0x0101 (2 b)
    # - Returns 0x5decb300
    # - Send color report (64 b)
    # - Send "flush" report (64 b, 2nd byte 0xb5)
    # - Returns 0x5decb300
    # - Send color report with 0xe1 in byte 7 (64 b)
    # - Returns 0x5decb500
    # - Send "flush" report (64 b, 2nd byte 0xb5)
    # - Returns 0x5decb300
    # - Returns 0x5decb500

    def __init__(self):
        super().__init__()
        self.color_report = ITEKeyboardReport()
        self.endpoint_out = 0x02
        self.endpoint_in = 0x81

    def static_color(self, red, green, blue, targets=None):
        """
        Change to a static color
        :param red: Red value, 0 - 255
        :param green: Green value, 0 - 255
        :param blue: Blue value, 0 - 255
        :param targets: Unused for the keyboard
        :return:
        """
        self.color_report.color(red, green, blue)

        xferred = self.color_report.send(self.handle)
        print('write K0: ', xferred)

        # ba_0101 = bytearray(2)
        # ba_0101[0] = 0x01
        # ba_0101[1] = 0x01
        # xferred = self.handle.interruptWrite(0x02, ba_0101, 2)
        # print('write K1: ', xferred)
