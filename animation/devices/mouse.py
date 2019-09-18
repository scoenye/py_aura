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
import threading
import time

from animation.effects import Effect, StrobeEffect, CycleEffect, RainbowEffect
from animation.generators import ConstantGenerator, LinearGenerator, QuadraticGenerator, \
    GeneratorState, CompositeGenerator, CompositeGeneratorRGB
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


class StrobeEffectGladius(StrobeEffect):
    """
    Strobe effect for the mouse
    """
    def _runnable(self):
        report = GladiusIIReport()

        if self.targets is None:
            self.targets = [GladiusIIMouse.LED_LOGO, GladiusIIMouse.LED_WHEEL, GladiusIIMouse.LED_BASE]

        while self.keep_running:
            for step in range(1, 16):
                report.color(0, 0, 0)

                for target in self.targets:
                    report.target(target)
                    self.device.write_interrupt(report)

                time.sleep(0.05)

            for step in self.color_steps:
                report.color(step[0], step[1], step[2])

                for target in self.targets:
                    report.target(target)
                    self.device.write_interrupt(report)

                time.sleep(0.05)

            time.sleep(0.05)


class CycleEffectGladius(CycleEffect):
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

        sw_byte_04 = 0

        self._preamble()

        hw_report.color(self.red, self.green, self.blue)
        hw_report.effect(GladiusIIReport.EFFECT_CYCLE)

        self._send_all_targets(hw_report)

        time.sleep(1)

        sw_report.color(sw_byte_04, 0, 0)               # Value may not be color related at all

        while self.keep_running:                        # 0x60 report does not seem to have any influence
            self.device.write_interrupt(sw_report)      # No targets in this thing...

            sw_byte_04 = (sw_byte_04 + 33) % 256

            sw_report.color(sw_byte_04, 0, 0)

            time.sleep(1)

        hw_report.effect(GladiusIIReport.EFFECT_NONE)   # Cancel the hardware cycle effect.
        self._send_all_targets(hw_report)

    def start(self, device, targets=None):
        targets = targets or [GladiusIIMouse.LED_LOGO, GladiusIIMouse.LED_WHEEL, GladiusIIMouse.LED_BASE]
        super().start(device, targets)


class RainbowEffectGladius(RainbowEffect):
    """
    Rainbow effect for the mouse
    """
    def __init__(self):
        super().__init__()
        red = CompositeGenerator()
        red.add_state(GeneratorState(ConstantGenerator, 0, 80, constant=255))
        red.add_state(GeneratorState(LinearGenerator, -40, 0, order1=-6.4, constant=-1))
        red.add_state(GeneratorState(ConstantGenerator, 0, 40, constant=0))
        red.add_state(GeneratorState(LinearGenerator, 0, 40, order1=6.4, constant=0))
        red.add_state(GeneratorState(ConstantGenerator, 0, 90, constant=255))

        green = CompositeGenerator()
        green.add_state(GeneratorState(ConstantGenerator, 0, 120, constant=0))
        green.add_state(GeneratorState(LinearGenerator, 0, 40, order1=6.4, constant=0))
        green.add_state(GeneratorState(ConstantGenerator, 0, 40, constant=255))
        green.add_state(GeneratorState(QuadraticGenerator, -80, 80, order2=0.04, order1=0, constant=0))
        green.add_state(GeneratorState(ConstantGenerator, 0, 40, constant=255))
        green.add_state(GeneratorState(LinearGenerator, -40, 0, order1=-6.4, constant=-1))
        green.add_state(GeneratorState(ConstantGenerator, 0, 120, constant=0))

        blue = CompositeGenerator()
        blue.add_state(GeneratorState(QuadraticGenerator, 0, 80, order2=0.04, order1=0, constant=0))
        blue.add_state(GeneratorState(ConstantGenerator, 0, 40, constant=255))
        blue.add_state(GeneratorState(LinearGenerator, -40, 0, order1=-6.4, constant=-1))
        blue.add_state(GeneratorState(ConstantGenerator, 0, 240, constant=0))
        blue.add_state(GeneratorState(LinearGenerator, 0, 40, order1=6.4, constant=0))
        blue.add_state(GeneratorState(ConstantGenerator, 0, 40, constant=255))
        blue.add_state(GeneratorState(QuadraticGenerator, -80, 0, order2=0.04, order1=0, constant=0))

        self.generator = CompositeGeneratorRGB(red, green, blue)

    def _runnable(self):
        report = GladiusIIReport()

        if self.targets is None:
            self.targets = [GladiusIIMouse.LED_LOGO, GladiusIIMouse.LED_WHEEL, GladiusIIMouse.LED_BASE]

        for color in self.generator.color():
            report.color(int(color[0]), int(color[1]), int(color[2]))

            for target in self.targets:
                report.target(target)
                self.device.write_interrupt(report)

            time.sleep(0.05)

            if not self.keep_running:
                break
