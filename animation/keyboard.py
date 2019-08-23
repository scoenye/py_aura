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

from animation.effects import Effect, StrobeEffect
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

        self._preamble()

        if self.targets is None:
            self.targets = [ITEKeyboard.LED_SEGMENT1, ITEKeyboard.LED_SEGMENT2, ITEKeyboard.LED_SEGMENT3,
                            ITEKeyboard.LED_SEGMENT4, ITEKeyboard.LED_SEGMENT5, ITEKeyboard.LED_SEGMENT6,
                            ITEKeyboard.LED_SEGMENT7]

        while self.keep_running:
            for step in range(1, 16):
                report.color(0, 0, 0, self.targets)

                self.device.write_interrupt(report)

                time.sleep(0.05)

            for step in self.color_steps:
                report.color(step[0], step[1], step[2], self.targets)

                self.device.write_interrupt(report)

                time.sleep(0.05)

            time.sleep(0.05)


class CycleEffectITE(Effect):
    """
    Cycle effect for the keyboard
    """
    def __init__(self):
        super().__init__()
        self.device = None
        self.targets = []
        self.thread = threading.Thread(target=self._runnable)
        self.keep_running = True

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

        self._preamble()

        cycle = 1

        while self.keep_running:                        # 0x5db6 report does not seem to have any influence
            time.sleep(1)

            cycle_report.cycle(cycle)
            self.device.write_interrupt(cycle_report)

            cycle = (cycle + 33) % 256

        self._wind_down()

    def start(self, device, targets=None):
        self.targets = targets
        self.device = device
        self.thread.start()

    def stop(self):
        self.keep_running = False
        self.thread.join()