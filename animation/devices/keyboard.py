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
import time

from animation.devices.common import RainbowBlockLine, RainbowCurvedLine, CycleCurve, StrobeCurve
from animation.effects import Effect, StrobeEffect, CycleEffect, RainbowEffect
from animation.generators import CompositeGeneratorRGB
from device import ITEKeyboard
from report import ITEKeyboardReport, ITEFlushReport, ITEKeyboardSegmentReport, ITEKeyboardCycleReport


class StaticEffectITE(Effect):
    """
    Single color change effect for ITE keyboard
    """

    def start(self, device, targets=None):
        color_report = ITEKeyboardReport()
        flush_report = ITEFlushReport()

        color_report.color(self.red, self.green, self.blue)

        xferred = device.write_interrupt(color_report)
        print('write K0: ', xferred)

        xferred = device.write_interrupt(color_report)
        print('write K1: ', xferred)

        xferred = device.write_interrupt(flush_report)  # Additional observation in strobe effect
        print('write K4: ', xferred)

        color_report.byte_7(0xe1)
        xferred = device.write_interrupt(color_report)
        print('write K3: ', xferred)

        xferred = device.write_interrupt(flush_report)
        print('write K4: ', xferred)


class StrobeEffectITE(StrobeEffect):
    """
    Strobe effect for the mouse
    """
    def _preamble(self):
        report = ITEKeyboardReport()
        report.color(self.red, self.green, self.blue)
        # report,byte_04(0x0a)
        self.device.write_interrupt(report)

    def _runnable(self):
        report = ITEKeyboardSegmentReport()

        generator = CompositeGeneratorRGB(
            StrobeCurve(0, self.red),
            StrobeCurve(0, self.green),
            StrobeCurve(0, self.blue))

        colors = generator.color()

        self._preamble()

        if self.targets is None:
            self.targets = [ITEKeyboard.LED_SEGMENT1, ITEKeyboard.LED_SEGMENT2, ITEKeyboard.LED_SEGMENT3,
                            ITEKeyboard.LED_SEGMENT4, ITEKeyboard.LED_SEGMENT5, ITEKeyboard.LED_SEGMENT6,
                            ITEKeyboard.LED_SEGMENT7]

        while self.keep_running:
            color = next(colors)

            report.color(color[0], color[1], color[2], self.targets)
            self.device.write_interrupt(report)

            time.sleep(0.05)


class CycleEffectITE(CycleEffect):
    """
    Cycle effect for the keyboard
    """
    def _preamble(self):
        color_report = ITEKeyboardReport()
        flush_report = ITEFlushReport()

        color_report.color(0xff, 0, 0)
        color_report.effect(ITEKeyboardReport.EFFECT_CYCLE)     # This is what makes the effect work.
        color_report.byte_7(0xeb)
        self.device.write_interrupt(color_report)

        color_report.color(0xff, 0xff, 0xff)
        color_report.byte_7(0xe1)
        self.device.write_interrupt(color_report)

        self.device.write_interrupt(flush_report)

        self.device.write_interrupt(color_report)

        self.device.write_interrupt(flush_report)

    def _wind_down(self):
        color_report = ITEKeyboardReport()
        flush_report = ITEFlushReport()

        color_report.color(0xff, 0xff, 0xff)
        self.device.write_interrupt(color_report)

        self.device.write_interrupt(color_report)

        self.device.write_interrupt(flush_report)

        color_report.byte_7(0xe1)

        self.device.write_interrupt(color_report)

        self.device.write_interrupt(flush_report)

    def _runnable(self):
        cycle_report = ITEKeyboardCycleReport()
        cycle_generator = CycleCurve(0)
        colors = cycle_generator.color()

        self._preamble()

        while self.keep_running:                        # 0x5db6 report does not seem to have any influence
            time.sleep(1)

            cycle = next(colors)
            cycle_report.cycle(cycle)
            self.device.write_interrupt(cycle_report)

        self._wind_down()


class RainbowEffectITE(RainbowEffect):
    """
    Rainbow effect for the keyboard
    """
    def __init__(self):
        super().__init__()
        self.segment1 = CompositeGeneratorRGB(RainbowBlockLine(112), RainbowCurvedLine(112), RainbowCurvedLine(432))
        self.segment2 = CompositeGeneratorRGB(RainbowBlockLine(75), RainbowCurvedLine(75), RainbowCurvedLine(395))
        self.segment3 = CompositeGeneratorRGB(RainbowBlockLine(37), RainbowCurvedLine(37), RainbowCurvedLine(357))
        self.segment4 = CompositeGeneratorRGB(RainbowBlockLine(0), RainbowCurvedLine(0), RainbowCurvedLine(320))

    def _preamble(self):
        report = ITEKeyboardReport()
        report.color(0, 0, 0)
        # report,byte_04(0x0a)
        self.device.write_interrupt(report)

    def _wind_down(self):
        color_report = ITEKeyboardReport()
        flush_report = ITEFlushReport()

        color_report.color(0xff, 0x00, 0xff)
        self.device.write_interrupt(color_report)
        self.device.write_interrupt(color_report)

        self.device.write_interrupt(flush_report)

        color_report.byte_7(0xe1)
        self.device.write_interrupt(color_report)

        self.device.write_interrupt(flush_report)

    def _runnable(self):
        report = ITEKeyboardSegmentReport()

        self._preamble()

        clear_targets = [ITEKeyboard.LED_SEGMENT5, ITEKeyboard.LED_SEGMENT6, ITEKeyboard.LED_SEGMENT7]

        colors1 = self.segment1.color()
        colors2 = self.segment2.color()
        colors3 = self.segment3.color()
        colors4 = self.segment4.color()

        while self.keep_running:
            color = next(colors1)
            report.color(color[0], color[1], color[2], [ITEKeyboard.LED_SEGMENT1, ITEKeyboard.LED_SEGMENT6])

            color = next(colors2)
            report.color(color[0], color[1], color[2], [ITEKeyboard.LED_SEGMENT2])

            color = next(colors3)
            report.color(color[0], color[1], color[2], [ITEKeyboard.LED_SEGMENT3, ITEKeyboard.LED_SEGMENT7])

            color = next(colors4)
            report.color(color[0], color[1], color[2], [ITEKeyboard.LED_SEGMENT4, ITEKeyboard.LED_SEGMENT5])
            self.device.write_interrupt(report)

            report.color(0, 0, 0, clear_targets)
            self.device.write_interrupt(report)

            time.sleep(0.01)

        self._wind_down()
