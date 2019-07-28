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


class Report:
    # All observed traces send 64 bytes, so that is what we start out with
    REPORT_SIZE = 64

    # Interesting offsets in the report structure
    REPORT_ID = 0

    # Observed values in the data transfers
    TYPE_GLADIUS = 0x51
    TYPE_ITE = 0x5d

    """
    Base class for reports to be sent to the USB peripherals
    """
    def __init__(self):
        self.report = bytearray(Report.REPORT_SIZE)
        self.endpoint_out = 0x00        # Override in subclass
        self.endpoint_in = 0x00         # Override in subclass

    def send(self, usb_handle):
        """
        Send the report to the device
        :param usb_handle: handle to open USB device
        :return:
        """
        return usb_handle.interruptWrite(self.endpoint_out, self.report, Report.REPORT_SIZE)


class GladiusIIReport(Report):
    # LED selector offset. Defined here as it may not be the same for other devices
    SELECT_LED = 2

    """
    Report class for the Gladius II mouse
    """
    def __init__(self):
        super().__init__()
        self.report[Report.REPORT_ID] = Report.TYPE_GLADIUS
        self.report[1] = 0x28
        self.report[5] = 0x04
        self.endpoint_out = 0x04
        self.endpoint_in = 0x83

    def color(self, red, green, blue):
        """
        Set the color to be sent to the device
        :param red: Red value, 0 - 255
        :param green: Green value, 0 - 255
        :param blue: Blue value, 0 - 255
        :return:
        """
        self.report[6] = red
        self.report[7] = green
        self.report[8] = blue

    def target(self, led):
        """
        Set the target LED for the color change
        :param led: LED selected for color change
        :return:
        """
        self.report[GladiusIIReport.SELECT_LED] = led


class ITEKeyboardReport(Report):
    """
    Report class for the Asus ITE keyboard
    """
    def __init__(self):
        super().__init__()
        self.report[Report.REPORT_ID] = Report.TYPE_ITE
        self.report[1] = 0xb3
        self.endpoint_out = 0x02
        self.endpoint_in = 0x81

    def color(self, red, green, blue):
        self.report[4] = red
        self.report[5] = green
        self.report[6] = blue

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


class FlushReport(Report):
    def __init__(self):
        super().__init__()
        self.report[Report.REPORT_ID] = Report.TYPE_ITE
        self.report[1] = 0xb5
        self.endpoint_out = 0x02
        self.endpoint_in = 0x81
