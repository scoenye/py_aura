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
from animation.keyboard import StaticEffectITE, CycleEffectITE, RainbowEffectITE
from animation.mouse import StaticEffectGladius, CycleEffectGladius

# find our device
# mouse = GladiusIIMouse()
keyboard = ITEKeyboard()

# mouse.open()
keyboard.open()

# mouse_static = StaticEffectGladius()
# mouse_static.color(0x00, 0xff, 0x00)
# mouse_static.start(mouse)  # Init the mouse LEDs
#
# mouse_static.color(0xff, 0x00, 0x00)
# mouse_static.start(mouse)
#
# kbd_static = StaticEffectITE()
# kbd_static.color(0xff, 0x00, 0xff)
# kbd_static.start(keyboard)
#
# mouse_cycle = CycleEffectGladius()
# keyboard_cycle = CycleEffectITE()
#
# mouse_cycle.color(0xff, 0x00, 0x00)
# keyboard_cycle.color(0xff, 0x00, 0x00)
#
# mouse_cycle.start(mouse)
# keyboard_cycle.start(keyboard)
#
keyboard_rainbow = RainbowEffectITE()
keyboard_rainbow.start(keyboard)
time.sleep(10)
#
# mouse_cycle.stop()
# keyboard_cycle.stop()
keyboard_rainbow.stop()
#
# mouse.close()
keyboard.close()
