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
from abc import ABC, abstractmethod


class ListUpdateListener(ABC):
    """
    Qt's model update API is one way: Qt models can update their underlying data source but there are no methods to
    make the model aware of an external change to the data source. This interface provides a way for models to
    receive notice of changes to the contents of their underlying data.
    """
    @abstractmethod
    def remove(self, index):
        """
        Signal an item needs to be removed from the list
        :param index: position of the item that needs to be removed
        :return:
        """

    @abstractmethod
    def insert(self, index):
        """
        Signal an item has been added to the list
        :param index: position where the item was inserted
        :return:
        """
