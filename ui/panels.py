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
from PySide2.QtCore import Signal


class CenterPanel(QtWidgets.QWidget):
    try_clicked = Signal(list, list, object)

    """
    Main window central widget
    """
    def __init__(self):
        super().__init__()
        self.main_layout = QtWidgets.QGridLayout(self)
        self.device_widget = QtWidgets.QListView()
        self.target_widget = QtWidgets.QListView()
        self.effect_widget = QtWidgets.QListView()
        self.color_widget = QtWidgets.QColorDialog()
        self.try_button = QtWidgets.QPushButton('&Try')

        # Allow selection of multiple devices
        self.device_widget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        # Hide OK/Cancel buttons on color picker
        self.color_widget.setOption(QtWidgets.QColorDialog.NoButtons, True)

        self._assemble_panel()
        self.setLayout(self.main_layout)

        self.try_button.clicked.connect(self._try_clicked)

    def _assemble_panel(self):
        self.main_layout.addWidget(self.device_widget, 0, 0)
        self.main_layout.addWidget(self.target_widget, 1, 0)
        self.main_layout.addWidget(self.effect_widget, 0, 1)
        self.main_layout.addWidget(self.color_widget, 0, 2)
        self.main_layout.addWidget(self.try_button, 2, 0)

    def _try_clicked(self):
        # Relay Try button click with all selected items
        self.try_clicked.emit(self.device_widget.selectedIndexes(),
                              self.effect_widget.selectedIndexes(),
                              self.color_widget.currentColor())

    def set_device_list(self, device_list):
        """
        Attach the model for the device list panel
        :param device_list:
        :return:
        """
        self.device_widget.setModel(device_list)
        self.device_widget.setCurrentIndex(device_list.index(0, 0))

    def set_effect_list(self, effect_list):
        """
        Attach the model for the effect list panel
        :return: effect_list
        """
        self.effect_widget.setModel(effect_list)
        self.effect_widget.setCurrentIndex(effect_list.index(0, 0))

    def add_try_listener(self, listener):
        """
        Add a listener interested in clicks on the Try button
        :param listener:
        :return:
        """
        # As long as the receiver is inside the Qt portion, use slot/signal.
        self.try_clicked.connect(listener)
