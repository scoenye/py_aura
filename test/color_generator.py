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

from animation.effects import ConstantGenerator, LinearGenerator


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
        for color in self.generator.color(0, 33):
            self.assertEqual(color, expected)
            expected += 8
