"""
    Nimbus USB
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
from PySide2 import QtCore
from PySide2.QtCore import Qt


class DeviceListModel(QtCore.QAbstractListModel):
    """
    Model for the DeviceListView
    """
    def __init__(self, devices=None):
        super().__init__()
        self.devices = devices

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.devices)

    def data(self, index, role: int = ...):
        if not index.isValid():
            return ''

        # Crucial as data() is called with almost every role in the book.
        if role != Qt.DisplayRole:
            return None

        return self.devices[index.row()]


class EffectListModel(QtCore.QAbstractListModel):
    """
    Model for the EffectListView
    """
    def __init__(self, effects=None):
        super().__init__()
        self.effects = effects

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.effects)

    def data(self, index, role: int = ...):
        if not index.isValid():
            return ''

        # Crucial as data() is called with almost every role in the book.
        if role != Qt.DisplayRole:
            return None

        return self.effects[index.row()]
