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

from animation.devices import keyboard as keyboard
from animation.effects import Effects, EffectContainer
from device.core import Device, LEDTarget


class ITEKeyboard(Device):
    """
    ASUS ITE keyboard (8910)
    """
    PRODUCT_ID = 0x1869

    EFFECT_MAP = {
        Effects.STATIC: EffectContainer(keyboard.StaticEffectHW, None),
        Effects.BREATHE: EffectContainer(keyboard.BreatheEffectHW, None),
        Effects.STROBE: EffectContainer(keyboard.StrobeEffectHW, keyboard.StrobeEffectSW),
        Effects.CYCLE: EffectContainer(keyboard.CycleEffectHW, keyboard.CycleEffectSW),
        Effects.RAINBOW: EffectContainer(keyboard.RainbowEffectHW, keyboard.RainbowEffectSW)
    }

    # Selectable segments
    LED_ALL = 0
    LED_SEGMENT1 = 1
    LED_SEGMENT2 = 2
    LED_SEGMENT3 = 3
    LED_SEGMENT4 = 4
    LED_SEGMENT5 = 5
    LED_SEGMENT6 = 6
    LED_SEGMENT7 = 7

    def __init__(self, bus_location, model):
        super().__init__(bus_location, model)
        self.targets = [
            LEDTarget(self, ITEKeyboard.LED_ALL, 'ALL'),
            LEDTarget(self, ITEKeyboard.LED_SEGMENT1, 'Segment 1'),      # The 4 hardware segments
            LEDTarget(self, ITEKeyboard.LED_SEGMENT2, 'Segment 2'),
            LEDTarget(self, ITEKeyboard.LED_SEGMENT3, 'Segment 3'),
            LEDTarget(self, ITEKeyboard.LED_SEGMENT4, 'Segment 4')
            # LEDTarget(self, ITEKeyboard.LED_SEGMENT5, 'SW Segment 5'),      # The extra undefined segments
            # LEDTarget(self, ITEKeyboard.LED_SEGMENT6, 'SW Segment 6'),      # used by the parallel report
            # LEDTarget(self, ITEKeyboard.LED_SEGMENT7, 'SW Segment 7')
        ]

    def selected_targets(self):
        """
        Return the list of selected targets for the device. Return the ALL target if no selection was made.
        :return: list of selected targets
        """
        base_list = super().selected_targets()          # The list of actually selected targets, if any.
        return base_list or [self.targets[ITEKeyboard.LED_ALL]]

    def parallel_targets(self):
        """
        Return the list of selected targets suitable for use by the parallel report(s). All targets are returned
        if no selection was made.
        :return: list of selected targets
        """
        base_list = super().selected_targets()

        if not base_list:       # No selection: use the colors as defined for the synthetic all target components
            base_list = [self.targets[ITEKeyboard.LED_SEGMENT1], self.targets[ITEKeyboard.LED_SEGMENT2],
                         self.targets[ITEKeyboard.LED_SEGMENT3], self.targets[ITEKeyboard.LED_SEGMENT4]]
        elif base_list == [self.targets[ITEKeyboard.LED_ALL]]:
            base_list = [self.targets[ITEKeyboard.LED_SEGMENT1], self.targets[ITEKeyboard.LED_SEGMENT2],
                         self.targets[ITEKeyboard.LED_SEGMENT3], self.targets[ITEKeyboard.LED_SEGMENT4]]

            # As there is no real ALL target (?), copy its color to the components
            for target in base_list:
                target.change_color(self.targets[ITEKeyboard.LED_ALL].color())  # TODO: tell the view?

        return base_list
