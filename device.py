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
from report import GladiusIIReport, ITEKeyboardReport, ITEFlushReport


class Device:
    """
    Base class for Aura USB devices
    """
    VENDOR_ID = 0x0b05
    PRODUCT_ID = 0x0000

    def __init__(self):
        self.handle = None
        self.aura_interface = 0
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

    def close(self):
        """
        Release the device
        :return:
        """
        self.handle.close()

    def write_interrupt(self, report, size):
        """
        Transmit the report to the device's Aura endpoint
        :param size: length of the block of data to send
        :param report: data to send to the device
        :return: number of bytes transferred to the device
        """
        kernel_attached = self.handle.kernelDriverActive(self.aura_interface)

        if kernel_attached:
            self.handle.detachKernelDriver(self.aura_interface)

        self.handle.claimInterface(self.aura_interface)

        try:
            transferred = self.handle.interruptWrite(self.endpoint_out, report, size)
        finally:
            self.handle.releaseInterface(self.aura_interface)
            if kernel_attached:
                self.handle.attachKernelDriver(self.aura_interface)

        return transferred

    def read_interrupt(self, size):
        """
        Request a return report from the device's Aura endpoint
        :param size: amount of data requested
        :return: data transmitted by the device
        """
        kernel_attached = self.handle.kernelDriverActive(self.aura_interface)

        if kernel_attached:
            self.handle.detachKernelDriver(self.aura_interface)

        self.handle.claimInterface(self.aura_interface)

        try:
            transferred = self.handle.interruptRead(self.endpoint_in, size)
        finally:
            self.handle.releaseInterface(self.aura_interface)
            if kernel_attached:
                self.handle.attachKernelDriver(self.aura_interface)

        return transferred


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
    # - Send color report (64 b)
    # - Send color report (64 b)
    # - Send color report with 0xe1 in byte 7 (64 b)
    # - Send "flush" report (64 b, 2nd byte 0xb5)

    def __init__(self):
        super().__init__()
        self.color_report = ITEKeyboardReport()
        self.flush_report = ITEFlushReport()
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

        xferred = self.color_report.send(self)
        print('write K0: ', xferred)

        xferred = self.color_report.send(self)
        print('write K1: ', xferred)

        self.color_report.byte_7_e1()
        xferred = self.color_report.send(self)
        print('write K3: ', xferred)

        xferred = self.flush_report.send(self)
        print('write K4: ', xferred)
