"""
    pyAura USB
    A tool to change the LED colors on ASUS Aura USB HID peripherals

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

from abc import ABC


class Report(ABC):
    # All observed traces send 64 bytes, so that is what we start out with
    REPORT_SIZE = 64

    REPORT_ID = 0       # Report identifier, specific to the device.
    REPORT_TYPE = 0     # Report subtype within the device class

    # Interesting offsets in the report structure
    OFFSET_ID = 0
    OFFSET_TYPE = 1

    """
    Base class for reports to be sent to the USB peripherals
    """
    def __init__(self):
        self.report = bytearray(Report.REPORT_SIZE)
        self.report[Report.OFFSET_ID] = self.REPORT_ID
        self.report[Report.OFFSET_TYPE] = self.REPORT_TYPE

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
    REPORT_ID = 0x51
    REPORT_TYPE = 0x28

    # Feature selector offsets. Defined here as they are not the same for other devices
    SELECT_LED = 2
    SELECT_EFFECT = 4
    SELECT_LEVEL = 5
    SELECT_COLOR = 6

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
        self.report[GladiusIIReport.SELECT_EFFECT] = GladiusIIReport.EFFECT_STATIC
        self.report[GladiusIIReport.SELECT_LEVEL] = GladiusIIReport.LEVEL_100

    def color(self, color_rgb):
        """
        Set the color to be sent to the device.
        :param color_rgb: 3-tuple with red/green/blue color components. Integer, range 0 - 255.
        :return:
        """
        self.report[GladiusIIReport.SELECT_COLOR:GladiusIIReport.SELECT_COLOR + 2] = color_rgb

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
    REPORT_ID = 0x60
    REPORT_TYPE = 0x01

    def __init__(self):
        super().__init__()
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
    REPORT_ID = 0x5d
    REPORT_TYPE = 0xb3      # Color set report

    """
    Report class for the ASUS ITE keyboard. This variation address the keyboard as a whole.
    """
    SELECT_SEGMENT = 2
    SELECT_EFFECT = 3
    SELECT_COLOR = 4

    # Built-in light effects
    EFFECT_STATIC = 0x00
    EFFECT_BREATHE = 0x01
    EFFECT_CYCLE = 0x02         # All segments, no color control
    EFFECT_RAINBOW = 0x03       # All segments, no color control.
    EFFECT_STROBE = 0x0a

    def color(self, color_rgb):
        """
        Set the color to be sent to the device.
        :param color_rgb: 3-tuple with red/green/blue color components. Integer, range 0 - 255.
        :return:
        """
        self.report[ITEKeyboardReport.SELECT_COLOR:ITEKeyboardReport.SELECT_COLOR + 2] = color_rgb

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
    REPORT_TYPE = 0xb4


class ITEKeyboardCycleReport(ITEKeyboardReport):
    REPORT_TYPE = 0xb6

    def __init__(self):
        super().__init__()
        self.report[2] = 0x02
        self.report[3] = 0x02

    def cycle(self, cycle):
        self.report[4] = cycle


class ITEKeyboardSegmentReport(Report):
    """
    Alternative ITE keyboard report which addresses different segments individually.
    """
    REPORT_ID = 0x5d  # This is an ITEKeyboardReport but the color method is off.
    REPORT_TYPE = 0xbc

    # Starting as a distinct report. May merge if there are sufficient commonalities.
    SEGMENT_OFFSETS = [9, 12, 15, 18, 21, 24, 28]

    def __init__(self):
        super().__init__()
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
    REPORT_TYPE = 0xb5
