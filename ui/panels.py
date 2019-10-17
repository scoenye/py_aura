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


class EffectListView(QtWidgets.QListView):
    """
    List of available effects. Not all devices may support all effects natively.
    """
    def __init__(self):
        super().__init__()
        model = models.EffectListModel(['static', 'strobe', 'cycle', 'rainbow'])
        self.setModel(model)


class CenterPanel(QtWidgets.QWidget):
    """
    Main window central widget
    """

    def __init__(self):
        super().__init__()
        self.main_layout = QtWidgets.QGridLayout(self)
        self.device_widget = QtWidgets.QListView()
        self.main_layout.addWidget(EffectListView(), 0, 1)      # TODO: move to _assemble_panel
        self._assemble_panel()
        self.setLayout(self.main_layout)

    def _assemble_panel(self):
        self.main_layout.addWidget(self.device_widget, 0, 0)

    def set_device_list(self, device_list):
        """
        Attach the model for the device list panel
        :param device_list:
        :return:
        """
        self.device_widget.setModel(device_list)
