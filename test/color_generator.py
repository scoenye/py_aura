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
        self.generator = ConstantGenerator(constant=123)

    def test_color(self):
        for color in self.generator.color(0, 1):
            self.assertEqual(color, 123)


class LinearGeneratorTest(unittest.TestCase):
    def setUp(self):
        self.generator = LinearGenerator(order1=8, constant=0)

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
        self.state = GeneratorState(ConstantGenerator, 0, 40, constant=128)
        self.state.start()

    def test_colors(self):
        step_count = 0

        for color in self.state.colors():
            self.assertEqual(color, 128)
            step_count += 1

            if step_count > 40:     # In case a generator hangs
                self.fail('GeneratorStateTest.test_colors: step count exceeded')

    def test_colors_initial(self):
        step_count = 0

        for color in self.state.colors(38):
            step_count += 1

        self.assertEqual(step_count, 40 - 38)


class CompositeGeneratorTest(unittest.TestCase):
    def setUp(self):
        self.generator = CompositeGenerator()
        self.generator.add_state(GeneratorState(ConstantGenerator, 0, 2, constant=128))
        self.generator.add_state(GeneratorState(ConstantGenerator, 0, 2, constant=255))

    def test_color(self):
        colors = self.generator.color()

        color = next(colors)
        self.assertEqual(color, 128)

        color = next(colors)
        self.assertEqual(color, 128)

        color = next(colors)
        self.assertEqual(color, 255)

        color = next(colors)
        self.assertEqual(color, 255)

        color = next(colors)
        self.assertEqual(color, 128)

        color = next(colors)
        self.assertEqual(color, 128)

        color = next(colors)
        self.assertEqual(color, 255)

        color = next(colors)
        self.assertEqual(color, 255)


class CompositeGeneratorOffsetTest(unittest.TestCase):
    def setUp(self):
        self.generator = CompositeGenerator(108)
        self.generator.add_state(GeneratorState(ConstantGenerator, 0, 100, constant=128))
        self.generator.add_state(GeneratorState(ConstantGenerator, 0, 10, constant=255))
        self.generator.add_state(GeneratorState(ConstantGenerator, 0, 2, constant=64))

    def test_color(self):
        colors = self.generator.color()

        color = next(colors)
        self.assertEqual(color, 255)

        color = next(colors)
        self.assertEqual(color, 255)

        color = next(colors)
        self.assertEqual(color, 64)


class CompositeGeneratorRGBTest(unittest.TestCase):
    def setUp(self):
        red = CompositeGenerator()
        red.add_state(GeneratorState(ConstantGenerator, 0, 2, constant=0))
        red.add_state(GeneratorState(ConstantGenerator, 0, 2, constant=128))

        green = CompositeGenerator()
        green.add_state(GeneratorState(ConstantGenerator, 0, 2, constant=32))
        green.add_state(GeneratorState(ConstantGenerator, 0, 2, constant=160))

        blue = CompositeGenerator()
        blue.add_state(GeneratorState(ConstantGenerator, 0, 2, constant=64))
        blue.add_state(GeneratorState(ConstantGenerator, 0, 2, constant=192))

        self.generator = CompositeGeneratorRGB(red, green, blue)

    def test_color(self):
        count = 0

        for color in self.generator.color():
            if count % 4 < 2:
                self.assertTupleEqual(color, (0, 32, 64))
            else:
                self.assertTupleEqual(color, (128, 160, 192))
            count += 1

            if count > 8:
                break
