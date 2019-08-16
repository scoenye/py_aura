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

    def size(self):
        """
        :return: length of the report
        """
        return len(self.report)

    def send(self, handle):
        """
        Send the report to the device Aura endpoint
        :param handle: handle to open HIDAPI device
        :return:
        """
        c_report = (ctypes.c_char * 64).from_buffer(self.report)

        return handle.write(c_report)


class GladiusIIReport(Report):
    """
    Report class for the Gladius II mouse
    """
    # LED selector offset. Defined here as it may not be the same for other devices
    SELECT_LED = 2
    SELECT_EFFECT = 4
    SELECT_LEVEL = 5

    # Built-in light effects
    EFFECT_NONE = 0x00
    EFFECT_IN_OUT = 0x01
    EFFECT_CYCLE = 0x02
    EFFECT_RAINBOW = 0x03      # All LEDs
    EFFECT_BTN_PULSE = 0x04
    EFFECT_RUNNING = 0x05

    # Intensity
    LEVEL_OFF = 0x00           # All LEDs off
    LEVEL_25 = 0x01            # All LEDs, 25%
    LEVEL_50 = 0x02            # All LEDs, 50%
    LEVEL_75 = 0x03            # All LEDs, 75%
    LEVEL_100 = 0x04           # All LEDs, 100%
    LEVEL_100_LW = 0x05        # Logo + wheel, 100%, bottom nearly off. (Same for any other value)

    def __init__(self):
        super().__init__()
        self.report[Report.REPORT_ID] = Report.TYPE_GLADIUS
        self.report[1] = 0x28
        self.report[GladiusIIReport.SELECT_EFFECT] = GladiusIIReport.EFFECT_NONE
        self.report[GladiusIIReport.SELECT_LEVEL] = GladiusIIReport.LEVEL_100

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


class GladiusIICycleReport(Report):
    """

    """
class ITEKeyboardReport(Report):
    """
    Report class for the Asus ITE keyboard. This variation address the keyboard as a whole.
    """
    # byte 04 has meaning. See Strobe sample in ITEKeyboardSegmentReport
    def __init__(self):
        super().__init__()
        self.report[Report.REPORT_ID] = Report.TYPE_ITE
        self.report[1] = 0xb3
        self.report[7] = 0x44

    def color(self, red, green, blue):
        self.report[4] = red
        self.report[5] = green
        self.report[6] = blue

    def byte_7_e1(self):           # TODO: figure out purpose and improve name
        self.report[7] = 0xe1


class ITEKeyboardSegmentReport(Report):
    """
    Alternative ITE keyboard report which addresses different segments individually.
    """
    # Starting as a distinct report. May merge if there are sufficient commonalities.
    SEGMENT_OFFSETS = [9, 12, 15, 18, 21, 24, 28]

    def __init__(self):
        super().__init__()
        self.report[Report.REPORT_ID] = Report.TYPE_ITE
        self.report[1] = 0xbc
        self.report[2] = 0x01
        self.report[3] = 0x01  # 0x00 in "setup" report

    def color(self, red, green, blue, targets=None):
        """
        Set the color to be sent to the device
        :param red: Red value, 0 - 255
        :param green: Green value, 0 - 255
        :param blue: Blue value, 0 - 255
        :return:
        """
        for target in targets:
            self.report[ITEKeyboardSegmentReport.SEGMENT_OFFSETS[target]:
                        ITEKeyboardSegmentReport.SEGMENT_OFFSETS[target] + 2] = [red, green, blue]


class ITEFlushReport(ITEKeyboardReport):
    """
    Causes the keyboard to revert to its stored color
    """
    def __init__(self):
        super().__init__()
        self.report[Report.REPORT_ID] = Report.TYPE_ITE
        self.report[1] = 0xb5
