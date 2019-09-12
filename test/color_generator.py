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
import unittest

from animation.generators import ConstantGenerator, LinearGenerator, QuadraticGenerator, GeneratorState, \
    CompositeGenerator, CompositeGeneratorRGB


class ConstantGeneratorTest(unittest.TestCase):
    def setUp(self):
        self.generator = ConstantGenerator(value=123)

    def test_color(self):
        for color in self.generator.color(0, 1):
            self.assertEqual(color, 123)


class LinearGeneratorTest(unittest.TestCase):
    def setUp(self):
        self.generator = LinearGenerator(slope=8, offset=0)

    def test_color(self):
        expected = 0
        for color in self.generator.color(0, 34):
            self.assertEqual(color, expected)
            expected += 8


class QuadraticGeneratorTest(unittest.TestCase):
    def setUp(self):
        self.generator = QuadraticGenerator(order2=0.04, order1=0, constant=0)

    def test_color(self):
        expected = 255
        x = -80.0

        for color in self.generator.color(-80, 81):
            self.assertEqual(color, expected)
            x += 1
            expected = min(255, 0.04 * x ** 2)


class GeneratorStateTest(unittest.TestCase):
    def setUp(self):
        self.state = GeneratorState(ConstantGenerator, 0, 40, value=128)
        self.state.start()

    def test_colors(self):
        step_count = 0

        for color in self.state.colors():
            self.assertEqual(color, 128)
            step_count += 1

            if step_count > 40:     # In case a generator hangs
                self.fail('GeneratorStateTest.test_colors: step count exceeded')


class CompositeGeneratorTest(unittest.TestCase):
    def setUp(self):
        self.generator = CompositeGenerator()
        self.generator.add_state(GeneratorState(ConstantGenerator, 0, 10, value=128))
        self.generator.add_state(GeneratorState(ConstantGenerator, 0, 10, value=255))

    def test_advance(self):
        self.generator.advance()                # Get things started
        for color in self.generator.color():
            self.assertEqual(color, 128)

        for color in self.generator.color():
            self.assertEqual(color, 255)

        for color in self.generator.color():
            self.assertEqual(color, 128)


class CompositeGeneratorRGBTest(unittest.TestCase):
    def setUp(self):
        red = CompositeGenerator()
        red.add_state(GeneratorState(ConstantGenerator, 0, 5, value=0))
        red.add_state(GeneratorState(ConstantGenerator, 0, 5, value=128))

        green = CompositeGenerator()
        green.add_state(GeneratorState(ConstantGenerator, 0, 5, value=32))
        green.add_state(GeneratorState(ConstantGenerator, 0, 5, value=160))

        blue = CompositeGenerator()
        blue.add_state(GeneratorState(ConstantGenerator, 0, 5, value=64))
        blue.add_state(GeneratorState(ConstantGenerator, 0, 5, value=192))

        self.generator = CompositeGeneratorRGB(red, green, blue)

    def test_color(self):
        self.generator.start()
        limit = 0

        for color in self.generator.color():
            print(color)
            limit += 1
            if limit > 10:
                break
