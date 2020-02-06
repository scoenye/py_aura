"""
    pyAura USB
    A tool to change the LED colors on ASUS Aura USB HID peripherals

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

from animation.devices import mouse as mouse
from animation.effects import Effects, EffectContainer
from device.core import Device, LEDTarget


class GladiusIIMouse(Device):
    """
    ASUS RoG Gladius II mouse
    """
    PRODUCT_ID = 0x1845
    INTERFACE = 2

    EFFECT_MAP = {
        Effects.STATIC: EffectContainer(mouse.StaticEffectHW, None),
        Effects.BREATHE: EffectContainer(mouse.BreatheEffectHW, None),
        Effects.STROBE: EffectContainer(None, mouse.StrobeEffectSW),
        Effects.CYCLE: EffectContainer(mouse.CycleEffectHW, mouse.CycleEffectSW),
        Effects.PULSE: EffectContainer(mouse.PulseEffectHW, None),
        Effects.RAINBOW: EffectContainer(mouse.RainbowEffectHW, mouse.RainbowEffectSW),
        Effects.RUNNING: EffectContainer(mouse.RunningEffectHW, None)
    }

    # Selectable LEDs
    LED_LOGO = 0x00     # Selects the logo LED
    LED_WHEEL = 0x01    # Selects the wheel LED
    LED_BASE = 0x02     # Selects the mouse base
    LED_ALL = 0x03      # Selects all LEDs

    def __init__(self, bus_location, model):
        super().__init__(bus_location, model)
        self.targets = [
            LEDTarget(self, GladiusIIMouse.LED_ALL, 'ALL'),
            LEDTarget(self, GladiusIIMouse.LED_LOGO, 'Logo'),
            LEDTarget(self, GladiusIIMouse.LED_WHEEL, 'Wheel'),
            LEDTarget(self, GladiusIIMouse.LED_BASE, 'Base')
        ]

    def selected_targets(self):
        """
        Return the list of selected targets for the device. Return the ALL target if no selection was made.
        :return: list of selected targets
        """
        base_list = super().selected_targets()          # The list of actually selected targets, if any.
        return base_list or [self.targets[GladiusIIMouse.LED_ALL]]
