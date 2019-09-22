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
from device import GladiusIIMouse
from report import GladiusIIReport, GladiusIICCReport


class StaticEffectGladius(Effect):
    """
    Single color change for mouse
    """
    def start(self, device, targets=None):
        report = GladiusIIReport()
        report.color(self.red, self.green, self.blue)

        if targets is None:
            targets = [GladiusIIMouse.LED_LOGO, GladiusIIMouse.LED_WHEEL, GladiusIIMouse.LED_BASE]

        for target in targets:
            report.target(target)
            device.write_interrupt(report)


class StrobeEffectGladius(RunnableEffect):
    """
    Strobe effect for the mouse
    """
    def _runnable(self):
        report = GladiusIIReport()

        generator = CompositeGeneratorRGB(
            StrobeCurve(0, self.red),
            StrobeCurve(0, self.green),
            StrobeCurve(0, self.blue))

        colors = generator.color()

        if self.targets is None:
            self.targets = [GladiusIIMouse.LED_LOGO, GladiusIIMouse.LED_WHEEL, GladiusIIMouse.LED_BASE]

        while self.keep_running:
            color = next(colors)

            report.color(color[0], color[1], color[2])
            self.device.write_interrupt(report)

            time.sleep(0.05)


class CycleEffectGladius(RunnableEffect):
    """
    Cycle effect for the mouse
    """
    def _send_all_targets(self, report):
        # Send the report to all active targets
        for target in self.targets:
            report.target(target)
            self.device.write_interrupt(report)

    def _preamble(self):
        report = GladiusIIReport()

        report.color(0x4d, 0x00, 0x6f)                      # From observation
        report.effect(GladiusIIReport.EFFECT_CYCLE)         # Pick hardware cycle effect

        self._send_all_targets(report)

        time.sleep(0.45)

        report.color(0xff, 0xff, 0xff)
        report.effect(GladiusIIReport.EFFECT_NONE)

        self._send_all_targets(report)

    def _runnable(self):
        hw_report = GladiusIIReport()
        sw_report = GladiusIICCReport()

        cycle_generator = CycleCurve(0)
        colors = cycle_generator.color()

        self._preamble()

        hw_report.color(self.red, self.green, self.blue)
        hw_report.effect(GladiusIIReport.EFFECT_CYCLE)

        self._send_all_targets(hw_report)

        time.sleep(1)

        while self.keep_running:                        # 0x60 report does not seem to have any influence
            self.device.write_interrupt(sw_report)      # No targets in this thing...

            sw_byte_04 = next(colors)                    # Value may not be color related at all

            sw_report.color(sw_byte_04, 0, 0)

            time.sleep(1)

        hw_report.effect(GladiusIIReport.EFFECT_NONE)   # Cancel the hardware cycle effect.
        self._send_all_targets(hw_report)

    def start(self, device, targets=None):
        targets = targets or [GladiusIIMouse.LED_LOGO, GladiusIIMouse.LED_WHEEL, GladiusIIMouse.LED_BASE]
        super().start(device, targets)


class RainbowEffectGladius(RunnableEffect):
    """
    Rainbow effect for the mouse
    """
    def _runnable(self):
        report = GladiusIIReport()
        generator = CompositeGeneratorRGB(RainbowBlockLine(112), RainbowCurvedLine(112), RainbowCurvedLine(432))
        colors = generator.color()

        if self.targets is None:
            self.targets = [GladiusIIMouse.LED_LOGO, GladiusIIMouse.LED_WHEEL, GladiusIIMouse.LED_BASE]

        while self.keep_running:
            color = next(colors)
            report.color(color[0], color[1], color[2])

            for target in self.targets:
                report.target(target)
                self.device.write_interrupt(report)

            time.sleep(0.01)
