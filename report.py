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
    TYPE_GLADIUS_CC = 0x60
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
    # Feature selector offsets. Defined here as they are not the same for other devices
    SELECT_LED = 2
    SELECT_EFFECT = 4
    SELECT_LEVEL = 5

    # Built-in light effects
    EFFECT_STATIC = 0x00
    EFFECT_BREATHE = 0x01
    EFFECT_CYCLE = 0x02
    EFFECT_RAINBOW = 0x03      # All LEDs
    EFFECT_PULSE = 0x04
    EFFECT_RUNNING = 0x05      # All LEDs

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
        self.report[GladiusIIReport.SELECT_EFFECT] = GladiusIIReport.EFFECT_STATIC
        self.report[GladiusIIReport.SELECT_LEVEL] = GladiusIIReport.LEVEL_100

    def color(self, color_rgb):
        """
        Set the color to be sent to the device.
        :param color_rgb: 3-tuple with red/green/blue color components. Integer, range 0 - 255.
        :return:
        """
        self.report[6] = color_rgb[0]
        self.report[7] = color_rgb[1]
        self.report[8] = color_rgb[2]

    def target(self, led):
        """
        Set the target LED for the color change
        :param led: LED selected for color change
        :return:
        """
        self.report[GladiusIIReport.SELECT_LED] = led

    def effect(self, effect):
        """
        Choose a hardware color effect
        :param effect: the code of the hardware effect to set
        :return:
        """
        self.report[GladiusIIReport.SELECT_EFFECT] = effect

    def level(self, level):
        """
        Choose a hardware intensity level
        :param level: the code of the hardware intensity level
        return:
        """
        self.report[GladiusIIReport.SELECT_LEVEL] = level


class GladiusIICCReport(Report):
    """
    Gladius report used by the Cycle effect
    """
    def __init__(self):
        super().__init__()
        self.report[Report.REPORT_ID] = Report.TYPE_GLADIUS_CC
        self.report[1] = 0x01
        self.report[5:63] = b'\xcc' * (63-5)

    def color(self, red, green, blue):
        """
        Set the color to be sent to the device
        :param red: Red value, 0 - 255
        :param green: Green value, 0 - 255
        :param blue: Blue value, 0 - 255
        :return:
        """
        self.report[4] = red        # These may not be color values
#        self.report[5] = green
#        self.report[6] = blue


class ITEKeyboardReport(Report):
    """
    Report class for the Asus ITE keyboard. This variation address the keyboard as a whole.
    """
    SELECT_SEGMENT = 2
    SELECT_EFFECT = 3

    # Built-in light effects
    EFFECT_STATIC = 0x00
    EFFECT_BREATHE = 0x01
    EFFECT_CYCLE = 0x02         # All segments, no color control
    EFFECT_RAINBOW = 0x03       # All segments, no color control.
    EFFECT_STROBE = 0x0a

    def __init__(self):
        super().__init__()
        self.report[Report.REPORT_ID] = Report.TYPE_ITE
        self.report[1] = 0xb3

    def color(self, color_rgb):
        """
        Set the color to be sent to the device.
        :param color_rgb: 3-tuple with red/green/blue color components. Integer, range 0 - 255.
        :return:
        """
        self.report[4] = color_rgb[0]
        self.report[5] = color_rgb[1]
        self.report[6] = color_rgb[2]

    def effect(self, effect):
        """
        Choose a hardware color effect
        :param effect: the code of the hardware effect to set
        :return:
        """
        self.report[ITEKeyboardReport.SELECT_EFFECT] = effect

    def target(self, segment):
        """
        Select a keyboard segment to address.
        :param segment: segment selected for color change
        :return:
        """
        self.report[ITEKeyboardReport.SELECT_SEGMENT] = segment

    def byte_7(self, value):           # TODO: figure out purpose and improve name
        self.report[7] = value


class ITEKeyboardApplyReport(ITEKeyboardReport):
    def __init__(self):
        super().__init__()
        self.report[1] = 0xb4


class ITEKeyboardCycleReport(ITEKeyboardReport):
    def __init__(self):
        super().__init__()
        self.report[1] = 0xb6
        self.report[2] = 0x02
        self.report[3] = 0x02

    def cycle(self, cycle):
        self.report[4] = cycle


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

    def color(self, colors, targets=None):
        """
        Set the color to be sent to the device
        :param colors: 3-tuple with red/green/blue color components. Integer, range 0 - 255.
        :param targets: segments affected by the color change
        :return:
        """
        # color is a tuple, which is iterable and so can be assigned to an array slice
        for target, color in zip(targets, colors):
            self.report[ITEKeyboardSegmentReport.SEGMENT_OFFSETS[target.target_segment() - 1]:
                        ITEKeyboardSegmentReport.SEGMENT_OFFSETS[target.target_segment() - 1] + 2] = color


class ITEFlushReport(ITEKeyboardReport):
    """
    Causes the keyboard to revert to its stored color
    """
    def __init__(self):
        super().__init__()
        self.report[Report.REPORT_ID] = Report.TYPE_ITE
        self.report[1] = 0xb5
