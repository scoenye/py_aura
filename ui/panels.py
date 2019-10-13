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
from PySide2 import QtWidgets

from ui import models


class DeviceListView(QtWidgets.QListView):
    """
    List of supported devices attached to the computer
    """
    def __init__(self):
        super().__init__()
        model = models.DeviceListModel(['mouse', 'keyboard'])
        self.setModel(model)


class EffectListView(QtWidgets.QListView):
    """
    List of available effects
    """


class CenterPanel(QtWidgets.QWidget):
    """
    Main window central widget
    """

    def __init__(self):
        super().__init__()
        self.main_layout = QtWidgets.QGridLayout(self)
        self.main_layout.addWidget(DeviceListView(), 0, 0)
        self.setLayout(self.main_layout)
