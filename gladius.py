"""
    gladius
    A demo program to change the ASUS RoG Gladius II mouse LED colors.

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
import udev

from device.mouse import GladiusIIMouse
from device.keyboard import ITEKeyboard
from animation.devices.keyboard import StaticEffectHW, RainbowEffectSW, CycleEffectSW, StrobeEffectSW
from animation.devices.mouse import StaticEffectHW, RainbowEffectSW, CycleEffectSW, StrobeEffectSW

from udev import USBEnumerator, USBMonitor
from device.containers import DeviceList

mouse_port = udev.NodeResolver.bus_location('/dev/hidraw2')
kbd_port = udev.NodeResolver.bus_location('/dev/hidraw4')

# enum = USBEnumerator()
# list = DeviceList()
#
# enum.add_listener(list)
# enum.enumerate()
#
# print(list.devices)
#
# monitor = USBMonitor()
# monitor.add_listener(list)
# monitor.start()
#
# time.sleep(10)
#
# monitor.stop()

# find our device
mouse = GladiusIIMouse(mouse_port, 'GladiusII')
keyboard = ITEKeyboard(kbd_port, 'ITEKeyboard')

mouse.open()
keyboard.open()

mouse_targets = mouse.show_targets()

# TODO: make addressing the target array friendlier
mouse_targets[1].select()
mouse_targets[1].change_color((255, 0, 0))
mouse_targets[2].select()
mouse_targets[2].change_color((0, 255, 0))
mouse_targets[3].select()
mouse_targets[3].change_color((0, 0, 255))

mouse_static = StaticEffectHW(mouse)
mouse_static.start()  # Init the mouse LEDs

# mouse_static.color(0xff, 0x00, 0x3f)
# mouse_static.start(mouse)

# kbd_static = StaticEffectHW(keyboard)
# kbd_static.start()
# kbd_static.apply()

# mouse_effect = StrobeEffectGladius()
# keyboard_effect = StrobeEffectITE()
#
# mouse_effect.start(mouse, [GladiusIIMouse.LED_LOGO])
# keyboard_effect.start(keyboard)

# mouse_effect = CycleEffectGladius()
# keyboard_effect = CycleEffectITE()
#
# mouse_effect.start(mouse)
# keyboard_effect.start(keyboard)

# mouse_effect = RainbowEffectGladius()
# mouse_effect.start(mouse, [GladiusIIMouse.LED_BASE])
#
# keyboard_effect = RainbowEffectITE()
# keyboard_effect.start(keyboard)

# time.sleep(10)

# mouse_effect.stop()
# keyboard_effect.stop()

# keyboard_effect.apply(keyboard)

mouse.close()
keyboard.close()

