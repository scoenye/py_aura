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
        device.set_color(self.red, self.green, self.blue, targets)


class StrobeEffect(Effect):
    """
    Strobe effect
    """
    def start(self, device, targets=None):
        # Interrupt interval: 0.05s
        # Set LED to 000000 (x14)  000000 (x15) 000000 (x16) 000000 (x16) 000000 (x15)
        #            060000        0c0000       05           0c           0c
        #            1a0000        21           1a           21           28
        #            2e0000        35           2e           35           42
        #            420000        4f           42           49           56
        #            560000        68           56           5c           68
        #            680000        7a           68           6e           7a
        #            7a0000        8b           7a           80           8b
        #            8b0000        9a           8b           90           9a
        #            9a0000        a8           9a           9f           ad
        #            a90000        b5           a8           ad           b9
        #            b50000        c1           b5           b9           c4
        #            c10000        ca           c4           c4           cd
        #            ca0000        d2           cd           cd           d4
        #            d20000        d8           d4           d4           da
        #            d80000        dd           da           da           de
        #            dd0000        df    0.1s   de           de           e0  0.1s
        #            df0000  0.1s               e0 0.1s      e0  0.1s
        for step in range(1, 16):
            device.set_color(0, 0, 0, targets)
            time.sleep(0.05)

        for step in (0x05, 0x1a, 0x2e, 0x42, 0x56, 0x68, 0x7a, 0x8b, 0x9a, 0xa8, 0xb5, 0xc4, 0xcd, 0xd4, 0xda, 0xde, 0xe0):
            device.set_color(step, step, step, targets)
            time.sleep(0.05)

        time.sleep(0.05)