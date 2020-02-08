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
from abc import ABC

from PySide2 import QtCore, QtGui
from PySide2.QtCore import Qt

from ui.assist import ListUpdateListener


# PySide2 uses a custom metaclass which makes it impossible to use Python's ABC class without extra work.
class ABCInterfaceBase(type(QtCore.QObject), type(ABC)):
    pass


class DeviceListModel(QtCore.QAbstractListModel, ListUpdateListener, metaclass=ABCInterfaceBase):
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

    def insertRows(self, row, count, parent=QtCore.QModelIndex()):
        self.beginInsertRows(parent, row, row + count)
        # Nothing in between as the row has already been inserted in the data source.
        self.endInsertRows()
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
        :param index: position of item removed from the model.
        :return:
        """
        self.removeRows(index, 1)

    def insert(self, index):
        """
        Called to signal a device was added to the system.
        :param index: position where the item is to be inserted in the model.
        :return:
        """
        self.insertRows(index, 1)


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


class TargetTableModel(QtCore.QAbstractTableModel, ListUpdateListener, metaclass=ABCInterfaceBase):
    """
    Model for the LED target color assignment
    """
    def __init__(self, devices):
        """
        :param devices: DeviceList holding the devices for which this model will show the target LEDs.
        """
        super().__init__()
        self.devices = devices

    def rowCount(self, parent=QtCore.QModelIndex()):
        # Returns the length of the longest set of targets across all devices.
        return self.devices.target_count()

    def columnCount(self, parent=QtCore.QModelIndex()):
        # Returns the total number of devices attached to the system.
        return len(self.devices)

    def headerData(self, section, orientation, role: int = ...):
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Orientation.Horizontal:
            return str(self.devices[section])

        return None

    def data(self, index, role: int = ...):
        if not index.isValid():
            return ''

        if role == Qt.DecorationRole:
            try:
                # devices[column] is also possible, but the target_name method is more in line with the other pieces
                # of the API and it does not expose the Device here.
                color_rgb = self.devices.target_color(index.column(), index.row())
                color = QtGui.QColor(color_rgb[0], color_rgb[1], color_rgb[2])
            except IndexError:
                color = None

            return color

        if role == Qt.DisplayRole:
            try:
                # Color retrieval comment applies here as well.
                element = self.devices.target_name(index.column(), index.row())
            except IndexError:
                element = None

            return element

        # For sll other roles
        return None

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            try:
                result = self.devices.change_color(index.column(), index.row(),
                                                   (value.red(), value.green(), value.blue()))
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
            self.devices.target_select(index.column(), index.row())

        for index in deselected.indexes():
            self.devices.target_deselect(index.column(), index.row())

    def remove(self, index):
        """
        Remove the targets for a device from the screen
        :param index:
        :return:
        """
        # Trying this here instead of overriding removeColumn to preserve it for Qt's intended reverse use
        self.beginRemoveColumns(QtCore.QModelIndex(), index, index)
        # Nothing in between as the device has already been removed from the data source.
        self.endRemoveColumns()
        return True

    def insert(self, index):
        """
        Insert a set of targets for a new device
        :param index:
        :return:
        """
        pass
