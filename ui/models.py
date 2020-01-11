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
from PySide2 import QtCore, QtGui
from PySide2.QtCore import Qt


class DeviceListModel(QtCore.QAbstractListModel):
    """
    Model for the DeviceListView
    """
    def __init__(self, devices=None):
        super().__init__()
        self.devices = devices
        self.devices.add_update_listener(self)      # For USB plug/unplug event notification

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.devices)

    def removeRows(self, row, count, parent=QtCore.QModelIndex()):
        self.beginRemoveRows(parent, row, row + count)
        # Nothing in between as the row has already been removed from the data source.
        self.endRemoveRows()
        return True

    def data(self, index, role: int = ...):
        if not index.isValid():
            return ''

        # Crucial as data() is called with almost every role in the book.
        if role == Qt.DisplayRole:
            return str(self.devices[index.row()])

        return None

    def selection_changed(self, selected, deselected):
        """
        Handle changes in the selection of devices
        :param selected: QItemSelection of devices newly selected
        :param deselected: QItemSelection of devices newly deselected
        :return:
        """
        for index in selected.indexes():
            self.devices.select(index.row())

        for index in deselected.indexes():
            self.devices.deselect(index.row())

    def remove(self, index):
        """
        Called to signal a device was removed from the system.
        :param index: position of item removed from the model's data
        :return:
        """
        self.removeRows(index, 1)


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
        self.targets = targets

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.targets)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return self.targets.device_count()

    def headerData(self, section, orientation, role: int = ...):
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Orientation.Horizontal:
            return self.targets.device_name(section)

        return None

    def data(self, index, role: int = ...):
        if not index.isValid():
            return ''

        if role == Qt.DecorationRole:
            try:
                # Ugly, but we aim to keep Qt dependencies out of the domain objects
                color_rgb = self.targets[index.column()][index.row()].color()
                color = QtGui.QColor(color_rgb[0], color_rgb[1], color_rgb[2])
            except IndexError:
                color = None

            return color

        if role == Qt.DisplayRole:
            try:
                element = self.targets[index.column()][index.row()].name()
            except IndexError:
                element = None

            return element

        # For sll other roles
        return None

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            try:
                element = self.targets[index.column()][index.row()]
                result = element.change_color((value.red(), value.green(), value.blue()))
            except IndexError:
                result = False
        else:
            result = False

        if result:
            self.dataChanged.emit(index, index, role)

        return result

    def selection_changed(self, selected, deselected):
        """
        Handle changes in the selection of targets
        :param selected: QItemSelection of targets newly selected
        :param deselected: QItemSelection of targets newly deselected
        :return:
        """
        for index in selected.indexes():
            self.targets.select(index.column(), index.row())

        for index in deselected.indexes():
            self.targets.deselect(index.column(), index.row())
