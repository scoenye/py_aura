"""
    Aura USB
    A tool to change the LED colors on Asus USB HID peripherals

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
from abc import ABC, abstractmethod
from collections import deque


class ColorGenerator(ABC):
    """
    Generate color values for effects
    """
    @abstractmethod
    def color(self, start, end):
        """
        :param start: starting position for the generator
        :param end: final position of the generator
        :return: a color value between 0 (black) and 255 (white)
        """


class ConstantGenerator(ColorGenerator):
    """
    Returns a constant value
    """
    def __init__(self, **kwargs):
        self.value = kwargs['value']

    def color(self, start, end):
        x = start
        while x < end:
            yield self.value
            x += 1


class LinearGenerator(ColorGenerator):
    """
    Advances in a straight line
    """
    def __init__(self, **kwargs):
        self.slope = kwargs['slope']
        self.offset = kwargs['offset']

    def color(self, start, end):
        x = start
        while x < end:
            yield self.slope * x + self.offset
            x += 1


class QuadraticGenerator(ColorGenerator):
    """
    Generate a parabolic curve
    """
    def __init__(self, **kwargs):
        self.order2 = kwargs['order2']
        self.order1 = kwargs['order1']
        self.constant = kwargs['constant']

    def color(self, start, end):
        x = start
        while x < end:
            yield min(255, self.order2 * x ** 2 + self.order1 * x + self.constant)  # Cap at 255
            x += 1


class GeneratorState:
    """
    Elementary piece of a composite color generation sequence
    """
    def __init__(self, generator, begin, end, **kwargs):
        """
        :param generator: ColorGenerator class which will create the color values for this step
        :param begin: starting ordinal value for the generator function
        :param end: ending ordinal value for the generator function
        :param **kwargs: parameters to pass to the generator's initializer
        """
        self.generator = generator
        self.generator_args = kwargs
        self.begin = begin
        self.end = end
        self.active_generator = None

    def start(self):
        """
        Initiate the generator
        :return:
        """
        self.active_generator = self.generator(**self.generator_args)

    def colors(self):
        """
        :return: the color generator instance for this step
        """
        return self.active_generator.color(self.begin, self.end)
