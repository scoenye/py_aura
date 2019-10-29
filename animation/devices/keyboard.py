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

import device as device_module

from animation.devices.common import RainbowBlockLine, RainbowCurvedLine, CycleCurve, StrobeCurve
from animation.effects import Effect, RunnableEffect
from animation.generators import CompositeGeneratorRGB
from report import ITEKeyboardReport, ITEFlushReport, ITEKeyboardSegmentReport, ITEKeyboardCycleReport, \
                ITEKeyboardApplyReport


class StaticEffectITE(Effect):
    """
    Single color change effect for ITE keyboard
    """

    def start(self, targets=None):
        color_report = ITEKeyboardReport()
        flush_report = ITEFlushReport()

        color_report.color((self.red, self.green, self.blue))

        targets = targets or [device_module.ITEKeyboard.LED_ALL]

        for target in targets:
            # Minimal required is 1 color report + 1 flush report
            color_report.target(target)
            self.device.write_interrupt(color_report)
            self.device.write_interrupt(color_report)
            self.device.write_interrupt(flush_report)

            color_report.byte_7(0xe1)
            self.device.write_interrupt(color_report)
            self.device.write_interrupt(flush_report)

    def apply(self):
        apply_report = ITEKeyboardApplyReport()
        flush_report = ITEFlushReport()

        self.device.write_interrupt(apply_report)
        self.device.write_interrupt(flush_report)


class ITERunnableEffect(RunnableEffect):
    """
    Keyboard specific RunnableEffect
    """
    def _wind_down(self):
        # Really just a change back to a single color
        color_report = ITEKeyboardReport()
        flush_report = ITEFlushReport()

        color_report.color((self.red, self.green, self.blue))
        self.device.write_interrupt(color_report)
        self.device.write_interrupt(color_report)
        self.device.write_interrupt(flush_report)

        color_report.byte_7(0xe1)
        self.device.write_interrupt(color_report)
        self.device.write_interrupt(flush_report)


class StrobeEffectITE(ITERunnableEffect):
    """
    Strobe effect for the mouse
    """
    def _preamble(self):
        report = ITEKeyboardReport()

        report.color((self.red, self.green, self.blue))     # Enables the hardware strobe effect, but the sequence
        report.effect(ITEKeyboardReport.EFFECT_STROBE)      # does nothing without a flush. No flush was observed
        self.device.write_interrupt(report)                 # in the trace.

    def _runnable(self):
        report = ITEKeyboardSegmentReport()

        generator = CompositeGeneratorRGB(
            StrobeCurve(0, self.red),
            StrobeCurve(0, self.green),
            StrobeCurve(0, self.blue))

        colors = generator.color()

        self.targets = self.targets or \
                       [device_module.ITEKeyboard.LED_SEGMENT1, device_module.ITEKeyboard.LED_SEGMENT2,
                        device_module.ITEKeyboard.LED_SEGMENT3, device_module.ITEKeyboard.LED_SEGMENT4,
                        device_module.ITEKeyboard.LED_SEGMENT5, device_module.ITEKeyboard.LED_SEGMENT6,
                        device_module.ITEKeyboard.LED_SEGMENT7]

        self._preamble()

        while self.keep_running:
            color = next(colors)

            report.color(color, self.targets)
            self.device.write_interrupt(report)

            time.sleep(0.05)

    def apply(self):
        flush_report = ITEFlushReport()

        self._preamble()
        self.device.write_interrupt(flush_report)


class CycleEffectITE(ITERunnableEffect):
    """
    Cycle effect for the keyboard
    """
    def _preamble(self):
        color_report = ITEKeyboardReport()
        flush_report = ITEFlushReport()

        color_report.color((0xff, 0, 0))
        color_report.effect(ITEKeyboardReport.EFFECT_CYCLE)     # Stages the hardware cycle effect.
        color_report.byte_7(0xeb)
        self.device.write_interrupt(color_report)

        color_report.color((0xff, 0xff, 0xff))
        color_report.byte_7(0xe1)
        self.device.write_interrupt(color_report)               # Cycle effect still set

        self.device.write_interrupt(flush_report)               # Enables the hardware cycle effect

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


class RainbowEffectITE(ITERunnableEffect):
    """
    Rainbow effect for the keyboard
    """
    def _preamble(self):
        report = ITEKeyboardReport()
        report.color((0, 0, 0))
        # report,byte_04(0x0a)
        self.device.write_interrupt(report)

    def _runnable(self):
        report = ITEKeyboardSegmentReport()

        self._preamble()

        clear_targets = [device_module.ITEKeyboard.LED_SEGMENT5, device_module.ITEKeyboard.LED_SEGMENT6,
                         device_module.ITEKeyboard.LED_SEGMENT7]

        self.targets = self.targets or \
                       [device_module.ITEKeyboard.LED_SEGMENT1, device_module.ITEKeyboard.LED_SEGMENT2,
                        device_module.ITEKeyboard.LED_SEGMENT3, device_module.ITEKeyboard.LED_SEGMENT4,
                        device_module.ITEKeyboard.LED_SEGMENT5, device_module.ITEKeyboard.LED_SEGMENT6,
                        device_module.ITEKeyboard.LED_SEGMENT7]

        segment1 = CompositeGeneratorRGB(RainbowBlockLine(112), RainbowCurvedLine(112), RainbowCurvedLine(432))
        segment2 = CompositeGeneratorRGB(RainbowBlockLine(75), RainbowCurvedLine(75), RainbowCurvedLine(395))
        segment3 = CompositeGeneratorRGB(RainbowBlockLine(37), RainbowCurvedLine(37), RainbowCurvedLine(357))
        segment4 = CompositeGeneratorRGB(RainbowBlockLine(0), RainbowCurvedLine(0), RainbowCurvedLine(320))

        colors1 = segment1.color()
        colors2 = segment2.color()
        colors3 = segment3.color()
        colors4 = segment4.color()

        while self.keep_running:
            color = next(colors1)
            report.color(color, [device_module.ITEKeyboard.LED_SEGMENT1, device_module.ITEKeyboard.LED_SEGMENT6])

            color = next(colors2)
            report.color(color, [device_module.ITEKeyboard.LED_SEGMENT2])

            color = next(colors3)
            report.color(color, [device_module.ITEKeyboard.LED_SEGMENT3, device_module.ITEKeyboard.LED_SEGMENT7])

            color = next(colors4)
            report.color(color, [device_module.ITEKeyboard.LED_SEGMENT4, device_module.ITEKeyboard.LED_SEGMENT5])
            self.device.write_interrupt(report)

            report.color((0, 0, 0), clear_targets)
            self.device.write_interrupt(report)

            time.sleep(0.01)

        self._wind_down()
