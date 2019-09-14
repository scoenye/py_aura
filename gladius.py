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
from animation.keyboard import StaticEffectITE, CycleEffectITE
from animation.mouse import StaticEffectGladius, CycleEffectGladius

from animation.generators import ConstantGenerator, GeneratorState, \
    CompositeGenerator, CompositeGeneratorRGB

red = CompositeGenerator()
red.add_state(GeneratorState(ConstantGenerator, 0, 5, value=0))
red.add_state(GeneratorState(ConstantGenerator, 0, 5, value=128))

green = CompositeGenerator()
green.add_state(GeneratorState(ConstantGenerator, 0, 5, value=32))
green.add_state(GeneratorState(ConstantGenerator, 0, 5, value=160))

blue = CompositeGenerator()
blue.add_state(GeneratorState(ConstantGenerator, 0, 5, value=64))
blue.add_state(GeneratorState(ConstantGenerator, 0, 5, value=192))

generator = CompositeGeneratorRGB(red, green, blue)

# generator.start()

limit = 0

for color in generator.color():
    print(color)
    limit += 1
    if limit > 20:
        break

# find our device
# mouse = GladiusIIMouse()
# keyboard = ITEKeyboard()
#
# mouse.open()
# keyboard.open()
#
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
# time.sleep(10)
#
# mouse_cycle.stop()
# keyboard_cycle.stop()
#
# mouse.close()
# keyboard.close()
