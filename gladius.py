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
import time

from device import GladiusIIMouse, ITEKeyboard
from animation import StaticEffect, StrobeEffect

# find our device
# mouse = GladiusIIMouse()
keyboard = ITEKeyboard()

# mouse.open()
keyboard.open()

# effect = StaticEffect()
# effect.color(0x00, 0x00, 0xff)
# effect.start(mouse, [GladiusIIMouse.LED_BASE, GladiusIIMouse.LED_WHEEL])  # Init the mouse LEDs

# mouse_strobe = StrobeEffect()

# mouse_strobe.color(0xff, 0x00, 0x00)
# mouse_strobe.start(mouse, [GladiusIIMouse.LED_LOGO])

keyboard_strobe = StrobeEffect()

keyboard_strobe.color(0xff, 0x00, 0x80)
keyboard_strobe.start(keyboard)

time.sleep(5)

# mouse_strobe.stop()

# time.sleep(5)

keyboard_strobe.stop()

# mouse.close()
keyboard.close()
