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
import time

import device as device_module

from animation.devices.common import RainbowBlockLine, RainbowCurvedLine, CycleCurve, StrobeCurve
from animation.effects import Effect, RunnableEffect
from animation.generators import CompositeGeneratorRGB
from report import ITEKeyboardReport, ITEFlushReport, ITEKeyboardSegmentReport, ITEKeyboardCycleReport, \
                ITEKeyboardApplyReport


# Effects with hardware support

class ITEEffectHW(Effect):
    """
    Static color change effect for ITE keyboard
    """
    EFFECT = None

    def start(self):
        color_report = ITEKeyboardReport()
        flush_report = ITEFlushReport()

        color_report.effect(self.EFFECT)

        for target in self.device.selected_targets():
            # Minimal required is 1 color report + 1 flush report
            color_report.color_target(target.target_segment(), target.color())
            self.device.write_interrupt(color_report)
            self.device.write_interrupt(flush_report)

            color_report.byte_7(0xe1)
            self.device.write_interrupt(color_report)
            self.device.write_interrupt(flush_report)

    def apply(self):
        """
        Make the current effect permanent.
        :return:
        """
        apply_report = ITEKeyboardApplyReport()
        flush_report = ITEFlushReport()

        self.start()    # Update hardware with whatever the user had selected

        self.device.write_interrupt(apply_report)
        self.device.write_interrupt(flush_report)


class StaticEffectHW(ITEEffectHW):
    """
    Static color change effect for ITE keyboard
    """
    EFFECT = ITEKeyboardReport.EFFECT_STATIC


class BreatheEffectHW(ITEEffectHW):
    """
    Breathing color change effect for ITE keyboard
    """
    EFFECT = ITEKeyboardReport.EFFECT_BREATHE


class CycleEffectHW(ITEEffectHW):
    """
    Cycle color change effect for ITE keyboard. Applies to all segments, Control over initial color only.
    """
    EFFECT = ITEKeyboardReport.EFFECT_CYCLE


class RainbowEffectHW(ITEEffectHW):
    """
    Rainbow color change effect for ITE keyboard. Applies to all segments, no control over color.
    """
    EFFECT = ITEKeyboardReport.EFFECT_RAINBOW


class StrobeEffectHW(ITEEffectHW):
    """
    Rainbow color change effect for ITE keyboard, Applies to all segments.
    """
    EFFECT = ITEKeyboardReport.EFFECT_STROBE


# Software based effects

class ITEEffectSW(RunnableEffect):
    """
    Keyboard specific RunnableEffect
    """
    def _wind_down(self):
        # Really just a change back to a single color. Used by CycleEffectSW and RainbowEffectSw which do not apply to
        # individual LED segments.
        color_report = ITEKeyboardReport()
        flush_report = ITEFlushReport()

        for target in self.targets:
            # Minimal required is 1 color report + 1 flush report
            color_report.color_target(target.target_segment(), target.color())
            self.device.write_interrupt(color_report)
            self.device.write_interrupt(flush_report)

            color_report.byte_7(0xe1)
            self.device.write_interrupt(color_report)
            self.device.write_interrupt(flush_report)


class StrobeEffectSW(ITEEffectSW):
    """
    Strobe effect for the mouse
    """
    def _preamble(self):
        report = ITEKeyboardReport()

        report.effect(ITEKeyboardReport.EFFECT_STROBE)

        for target in self.device.selected_targets():
            # Stages the hardware strobe effect, but the sequence does nothing without a flush. No flush was observed
            # in the trace.
            report.color_target(target.target_segment(), target.color())
            self.device.write_interrupt(report)

    def _runnable(self):
        report = ITEKeyboardSegmentReport()
        generators = []

        self.targets = self.device.parallel_targets()

        # Create a set of color generators for each selected target
        for target in self.targets:
            generators.append(CompositeGeneratorRGB(
                StrobeCurve(0, target.color()[0]),  # TODO: rework hardcoded indices
                StrobeCurve(0, target.color()[1]),
                StrobeCurve(0, target.color()[2])))

        colors = [generator.color() for generator in generators]

        self._preamble()

        while self.keep_running:
            step_colors = [next(color) for color in colors]

            for target, color in zip(self.targets, step_colors):
                report.color_target(target.target_segment(), color)

            self.device.write_interrupt(report)

            time.sleep(0.05)

    def apply(self):
        flush_report = ITEFlushReport()

        self._preamble()
        self.device.write_interrupt(flush_report)


class CycleEffectSW(ITEEffectSW):
    """
    Cycle effect for the keyboard
    """
    def _preamble(self):
        color_report = ITEKeyboardReport()
        flush_report = ITEFlushReport()

        color_report.effect(ITEKeyboardReport.EFFECT_CYCLE)     # Stages the hardware cycle effect.
        color_report.color_target(self.device.LED_ALL, (0xff, 0, 0))    # Cycle effect does not care about target
        color_report.byte_7(0xeb)

        self.device.write_interrupt(color_report)

        color_report.color_target(self.device.LED_ALL, (0xff, 0xff, 0xff))
        color_report.byte_7(0xe1)

        self.device.write_interrupt(color_report)               # Cycle effect still set
        self.device.write_interrupt(flush_report)               # Enables the hardware cycle effect

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


class RainbowEffectSW(ITEEffectSW):
    """
    Rainbow effect for the keyboard
    """
    def _preamble(self):
        report = ITEKeyboardReport()
        report.color_target(self.device.LED_ALL, (0, 0, 0))
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
            colors = next(colors1)
            report.color_target(device_module.ITEKeyboard.LED_SEGMENT1, colors)
            report.color_target(device_module.ITEKeyboard.LED_SEGMENT6, colors)

            colors = next(colors2)
            report.color_target(device_module.ITEKeyboard.LED_SEGMENT2, colors)

            colors = next(colors3)
            report.color_target(device_module.ITEKeyboard.LED_SEGMENT3, colors)
            report.color_target(device_module.ITEKeyboard.LED_SEGMENT7, colors)

            colors = next(colors4)
            report.color_target(device_module.ITEKeyboard.LED_SEGMENT4, colors)
            report.color_target(device_module.ITEKeyboard.LED_SEGMENT5, colors)

            self.device.write_interrupt(report)

            for target in clear_targets:
                report.color_target(target, (0, 0, 0))

            self.device.write_interrupt(report)

            time.sleep(0.01)

        self._wind_down()
