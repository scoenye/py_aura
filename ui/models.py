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
from PySide2 import QtCore, QtGui
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
        if role == Qt.DisplayRole:
            return self.devices[index.row()]

        return None


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
        if role == Qt.DisplayRole:
            return self.effects[index.row()]

        return None


class TargetTableModel(QtCore.QAbstractTableModel):
    """
    Model for the LED target color assignment
    """
    def __init__(self, targets=None):
        super().__init__()
        self.headers = ['Mouse', 'Keyboard']
        self.row_count = 4
        self.targets = targets

    def rowCount(self, parent=QtCore.QModelIndex()):
        return self.row_count

    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self.headers)

    def headerData(self, section, orientation, role: int = ...):
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Orientation.Horizontal:
            return self.headers[section]

        return None

    def data(self, index, role: int = ...):
        if not index.isValid():
            return ''

        if role == Qt.DecorationRole:
            return QtGui.QColor(255, 0, 0)

        if role == Qt.DisplayRole:
            return self.targets[index.column()][index.row()]

        return None
