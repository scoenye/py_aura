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
import threading

from report import GladiusIIReport, ITEKeyboardReport, ITEFlushReport
from device import GladiusIIMouse


class Effect:
    """
    Base class for lighting effects
    """
    def __init__(self):
        self.red = None
        self.green = None
        self.blue = None

    def color(self, red, green, blue):
        """
        Set the color for the effect
        :param red: Red value, 0 - 255
        :param green: Green value, 0 - 255
        :param blue: Blue value, 0 - 255
        :return:
        """
        self.red = red
        self.green = green
        self.blue = blue

    def start(self, device, targets=None):
        """
        Start execution of the effect
        :param device: Device to apply the effect to.
        :param targets: list of LEDs to change color of, None to change all LEDs
        :return:
        """


class StaticEffect(Effect):
    """
    Single color change
    """
    def start(self, device, targets=None):
        device.stage_color(self.red, self.green, self.blue, targets)
        device.change_color()


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

        color_report.byte_7_e1()
        xferred = device.write_interrupt(color_report)
        print('write K3: ', xferred)

        xferred = device.write_interrupt(flush_report)
        print('write K4: ', xferred)


class StrobeEffect(Effect):
    """
    Strobe effect
    """
    STEPS = [0.02, 0.10, 0.18, 0.26, 0.34, 0.41, 0.48, 0.54, 0.60, 0.66, 0.71, 0.77, 0.80, 0.83, 0.85, 0.87, 0.88]

    def __init__(self):
        super().__init__()
        self.device = None
        self.targets = []
        self.thread = threading.Thread(target=self._runnable)
        self.keep_running = True
        self.color_steps = []

    def color(self, red, green, blue):
        super().color(red, green, blue)

        # Reset step store
        self.color_steps = []

        # Pre-calculate the strobe steps for the user's RGB combination
        for step in self.STEPS:
            self.color_steps.append(
                (int(self.red * step), int(self.green * step), int(self.blue * step))
            )

    def _runnable(self):
        # Core of the strobe effect thread
        pass

    def start(self, device, targets=None):
        self.device = device
        self.targets = targets
        self.thread.start()

    def stop(self):
        self.keep_running = False
        self.thread.join()


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
