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
from itertools import chain


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
        self.value = kwargs['constant']

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
        self.slope = kwargs['order1']
        self.offset = kwargs['constant']

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
        # Generators cannot be reset -> must generate a new one every time
        self.active_generator = self.generator(**self.generator_args)

    def colors(self):
        """
        :return: the color generator instance for this step
        """
        yield from self.active_generator.color(self.begin, self.end)


class CompositeGenerator:
    """
    Combine a number of generators and switch between them. This class generates values for a single color.
    """
    def __init__(self):
        self.states = deque([])     # Collection of all states
        self.state = None           # Currently active state

    def add_state(self, state):
        """
        Append a GeneratorState to execution sequence. Generators will be loaded in order they were appended. When the
        last state in the sequence is reached, it will restart with the first.
        :param state: GeneratorState to add.
        :return:
        """
        self.states.append(state)

    def _advance(self):
        """
        Move to the next state in sequence
        :return:
        """
        while True:
            self.state = self.states.popleft()
            self.states.append(self.state)

            self.state.start()
            yield self.state.colors()

    def color(self):
        """
        :return: a color value from the current generator state
        """
        yield from chain.from_iterable(self._advance())


class CompositeGeneratorRGB:
    """
    Combine CompositeGenerators for red, green and blue colors
    """
    def __init__(self, red, green, blue):
        """
        :param red: CompositeGenerator for the red color values
        :param green: CompositeGenerator for the green color values
        :param blue: CompositeGenerator for the blue color values
        """
        self.generators = {'red': red, 'green': green, 'blue': blue}

    def color(self):
        """
        :return: a 3-tuple of reg/green/blue colors obtained from the component generators
        """
        rgb = zip(self.generators['red'].color(),
                  self.generators['green'].color(),
                  self.generators['blue'].color())

        yield from rgb
