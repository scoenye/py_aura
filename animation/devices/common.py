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
from animation.generators import CompositeGenerator, GeneratorState, ConstantGenerator, LinearGenerator, \
    QuadraticGenerator, CycleGenerator, StrobeGenerator


class RainbowBlockLine(CompositeGenerator):
    """
    Canonical "square wave" line for the keyboard rainbow effect
    """
    def __init__(self, initial=0):
        super().__init__(initial)
        self.add_state(GeneratorState(ConstantGenerator, 0, 160, constant=255))
        self.add_state(GeneratorState(LinearGenerator, -40, 0, order1=-6.4, constant=-1))
        self.add_state(GeneratorState(ConstantGenerator, 0, 80, constant=0))
        self.add_state(GeneratorState(LinearGenerator, 0, 40, order1=6.4, constant=0))


class RainbowCurvedLine(CompositeGenerator):
    """
    Canonical quadratic curve sequence for the keyboard rainbow effect
    """
    def __init__(self, initial=0):
        super().__init__(initial)
        self.add_state(GeneratorState(QuadraticGenerator, -80, 80, order2=0.04, order1=0, constant=0))
        self.add_state(GeneratorState(ConstantGenerator, 0, 80, constant=255))
        self.add_state(GeneratorState(LinearGenerator, -40, 0, order1=-6.4, constant=-1))
        self.add_state(GeneratorState(ConstantGenerator, 0, 240, constant=0))
        self.add_state(GeneratorState(LinearGenerator, 0, 40, order1=6.4, constant=0))
        self.add_state(GeneratorState(ConstantGenerator, 0, 80, constant=255))


class CycleCurve(CompositeGenerator):
    """
    Infinite cycle generator
    """
    def __init__(self, initial=0):
        super().__init__(initial)
        self.add_state(GeneratorState(CycleGenerator, 0, constant=33))


class StrobeCurve(CompositeGenerator):
    """
    Strobe effect color curve
    """
    def __init__(self, initial=0, color=255):
        super().__init__(initial)
        self.add_state(GeneratorState(ConstantGenerator, 0, 17, constant=0))
        self.add_state(GeneratorState(StrobeGenerator, 0, constant=color))
