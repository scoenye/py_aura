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


class CenterPanel(QtWidgets.QWidget):
    """
    Main window central widget
    """
    def __init__(self):
        super().__init__()
        self.main_layout = QtWidgets.QGridLayout(self)
        self.device_widget = QtWidgets.QListView()
        self.effect_widget = QtWidgets.QListView()
        self._assemble_panel()
        self.setLayout(self.main_layout)

    def _assemble_panel(self):
        self.main_layout.addWidget(self.device_widget, 0, 0)
        self.main_layout.addWidget(self.effect_widget, 0, 1)

    def set_device_list(self, device_list):
        """
        Attach the model for the device list panel
        :param device_list:
        :return:
        """
        self.device_widget.setModel(device_list)

    def set_effect_list(self, effect_list):
        """
        Attach the model for the effect list panel
        :return: effect_list
        """
        self.effect_widget.setModel(effect_list)
