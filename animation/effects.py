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
import threading

from enum import Enum


class Effects(Enum):
    STATIC = 0
    BREATHE = 1
    STROBE = 2
    CYCLE = 3
    RAINBOW = 4
    PULSE = 5
    RUNNING = 6


class Implementation(Enum):
    HARDWARE = 0
    SOFTWARE = 1


EFFECTS = [
    {'effect': Effects.STATIC, 'name': 'Static'},
    {'effect': Effects.BREATHE, 'name': 'Breathe'},
    {'effect': Effects.STROBE, 'name': 'Strobe'},
    {'effect': Effects.CYCLE, 'name': 'Cycle'},
    {'effect': Effects.RAINBOW, 'name': 'Rainbow'},
    {'effect': Effects.PULSE, 'name': 'Pulse'},
    {'effect': Effects.RUNNING, 'name': 'Running'}
]


class Effect:
    """
    Base class for lighting effects
    """
    def __init__(self, device):
        """
        :param device: hardware device to which this effect instance applies to.
        """
        self.device = device

    def start(self):
        """
        Start execution of the effect
        :return:
        """
        pass

    def stop(self):
        """
        Halt execution of the effect
        :return:
        """
        pass

    def apply(self):
        """
        Make the effect permanent (if the device supports it.)
        :return:
        """
        pass


class RunnableEffect(Effect):
    """
    Threaded lighting effect
    """
    def __init__(self, device):
        super().__init__(device)
        self.targets = []
        self.thread = threading.Thread(target=self._runnable)
        self.keep_running = True

    def _runnable(self):
        # Core of the strobe effect thread
        pass

    def start(self):
        """
        Start the execution of the effect as a separate thread.
        :return:
        """
        self.targets = self.device.selected_targets()
        self.thread.start()

    def stop(self):
        """
        Signal the thread to stop running.
        :return:
        """
        self.keep_running = False
        self.thread.join()


class NullEffect(Effect):
    """
    Do nothing placeholder for effects not supported by a device
    """


class EffectList:
    """
    List of available effects
    """
    def __len__(self):
        return len(EFFECTS)

    def __getitem__(self, item):
        return EFFECTS[item]['name']

    def instance(self, selection):
        """
        Convert the user selection into an effect descriptor
        :param selection: list with the selected effect index
        :return: effect descriptor
        """
        # Rather simplistic but we may not be done yet with the definition of the effect list itself.
        return EFFECTS[selection[0]]['effect']


class EffectContainer:
    def __init__(self, hw_effect, sw_effect):
        self.effects = {
            Implementation.HARDWARE: hw_effect,
            Implementation.SOFTWARE: sw_effect
        }

    def effect(self, implementation):
        """
        Return an effect implementation class.
        :param implementation: which implementation to return
        :return: desired implementing class.
        """
        return self.effects[implementation]
