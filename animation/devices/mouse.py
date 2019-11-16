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
from animation.effects import Effect, RunnableEffect
from animation.generators import CompositeGeneratorRGB
from report import GladiusIIReport, GladiusIICCReport


# Hardware backed effects

class StaticEffectHW(Effect):
    """
    Static color change for mouse
    """
    def start(self, targets=None):
        report = GladiusIIReport()
        report.effect(GladiusIIReport.EFFECT_STATIC)

        for target in self.device.selected_targets():
            report.target(target.target_segment())
            report.color(target.color())
            self.device.write_interrupt(report)


# Software based effects

class GladiusRunnableEffect(RunnableEffect):
    """
    Mouse specific RunnableEffect
    """
    def _send_all_targets(self, report, colors):
        # Send the report to all active targets
        for target, color in zip(self.targets, colors):
            report.target(target.target_segment())
            report.color(color)
            self.device.write_interrupt(report)


class StrobeEffectGladius(GladiusRunnableEffect):
    """
    Strobe effect for the mouse
    """
    def _runnable(self):
        report = GladiusIIReport()
        generators = []

        # Create a set of color generators for each selected target
        for target in self.targets:
            generators.append(CompositeGeneratorRGB(
                StrobeCurve(0, target.color()[0]),      # TODO: rework hardcoded indices
                StrobeCurve(0, target.color()[1]),
                StrobeCurve(0, target.color()[2])))

        colors = [generator.color() for generator in generators]

        # End of preamble - start effect
        while self.keep_running:
            step_colors = [next(color) for color in colors]
            self._send_all_targets(report, step_colors)

            time.sleep(0.05)


class CycleEffectGladius(GladiusRunnableEffect):
    """
    Cycle effect for the mouse
    """
    def _preamble(self):
        report = GladiusIIReport()

        colors = [target.color() for target in self.targets]
        report.effect(GladiusIIReport.EFFECT_CYCLE)         # Pick hardware cycle effect

        self._send_all_targets(report, colors)

        time.sleep(0.45)

        colors = [(0xff, 0xff, 0xff) for target in self.targets]
        report.effect(GladiusIIReport.EFFECT_STATIC)

        self._send_all_targets(report, colors)

    def _runnable(self):
        hw_report = GladiusIIReport()
        sw_report = GladiusIICCReport()

        cycle_generator = CycleCurve(0)     # Only used by the software report
        sw_colors = cycle_generator.color()

        self._preamble()

        hw_colors = [target.color() for target in self.targets]
        hw_report.effect(GladiusIIReport.EFFECT_CYCLE)

        self._send_all_targets(hw_report, hw_colors)

        time.sleep(1)

        while self.keep_running:                        # 0x60 report does not seem to have any influence
            self.device.write_interrupt(sw_report)      # No targets in this thing...

            sw_byte_04 = next(sw_colors)                    # Value may not be color related at all

            sw_report.color(sw_byte_04, 0, 0)

            time.sleep(1)

        hw_report.effect(GladiusIIReport.EFFECT_STATIC)   # Cancel the hardware cycle effect.
        self._send_all_targets(hw_report, hw_colors)    # Reset to colors chosen by the user


class RainbowEffectGladius(GladiusRunnableEffect):
    """
    Rainbow effect for the mouse
    """
    def _runnable(self):
        report = GladiusIIReport()
        generators = []

        # TODO: work out a way to start the effect with the selected colors
        for target in self.targets:
            generators.append(CompositeGeneratorRGB(
                RainbowBlockLine(112),          # Red component
                RainbowCurvedLine(112),         # Green component
                RainbowCurvedLine(432)))        # Blue component

        colors = [generator.color() for generator in generators]

        while self.keep_running:
            step_colors = [next(color) for color in colors]
            self._send_all_targets(report, step_colors)

            time.sleep(0.01)
