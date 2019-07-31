"""
    gladius
    A demo program to change the Asus RoG Gladius II mouse LED colors.

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

import usb1
import time

from device import GladiusIIMouse, ITEKeyboard
from animation import StaticEffect

# find our device
with usb1.USBContext() as context:

    mouse = GladiusIIMouse()

    mouse.open(context)

    effect = StaticEffect()
    effect.color(0xff, 0x00, 0x00)
    effect.start(mouse, [GladiusIIMouse.LED_LOGO, GladiusIIMouse.LED_WHEEL])

    time.sleep(1)

    effect.color(0x00, 0x00, 0xff)
    effect.start(mouse, [GladiusIIMouse.LED_BASE])

    mouse.close()

    keyboard = ITEKeyboard()

    keyboard.open(context)

    effect.start(keyboard)

    keyboard.close()
