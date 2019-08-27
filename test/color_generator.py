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

from animation.effects import HighGenerator, LowGenerator


class HighGeneratorTest(unittest.TestCase):
    def setUp(self):
        self.generator = HighGenerator()

    def test_color(self):
        for color in self.generator.color():
            self.assertEqual(color, 255)
            break   # This generator never ends


class LowGeneratorTest(unittest.TestCase):
    def setUp(self):
        self.generator = LowGenerator()

    def test_color(self):
        for color in self.generator.color():
            self.assertEqual(color, 0)
            break   # This generator never ends
