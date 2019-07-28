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

from device import GladiusIIMouse

# find our device
with usb1.USBContext() as context:

    mouse = GladiusIIMouse()

    mouse.open(context)

    mouse.static_color(0x80, 0x80, 0x80)        # Change all colors

    time.sleep(1)

    mouse.static_color(0x00, 0xff, 0x80, [GladiusIIMouse.LED_BASE])

    time.sleep(1)

    mouse.static_color(0x80, 0x00, 0xff, [GladiusIIMouse.LED_WHEEL])

    time.sleep(1)

    mouse.static_color(0xff, 0x00, 0x00, [GladiusIIMouse.LED_LOGO])

    time.sleep(1)

    mouse.static_color(0x80, 0x80, 0x00, [GladiusIIMouse.LED_BASE, GladiusIIMouse.LED_WHEEL])

#    xferred = handle_mouse.interruptRead(0x83, 64)
#    print('read M0: ', xferred.hex())

#    xferred = handle.interruptRead(0x83, 64)
#    print('read 1: ', xferred)

#    xferred = handle.interruptRead(0x83, 64)
#    print('read 2: ', xferred)

    mouse.close()
