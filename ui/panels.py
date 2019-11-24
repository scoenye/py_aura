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


class DeviceListView(QtWidgets.QListView):
    """
    ListView to show the devices and control the target view
    """
    def __init__(self, parent):
        super().__init__(parent)
        # Allow selection of multiple devices
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

    def selectionChanged(self, selected, deselected):
        # selected and deselected are deltas. Whatever comes in selected needs to be enabled in the target list,
        # whatever is in deselected needs to be disabled,
        super().selectionChanged(selected, deselected)
        self.model().selection_changed(selected, deselected)


class TargetTableView(QtWidgets.QTableView):
    """
    Show the targetable LEDs for all devices. Targets on selected devices are enabled, targets on deselected devices
    are disabled.
    """
    def __init__(self, parent):
        super().__init__(parent)
        # Allow selection of multiple targets
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

    def color_change(self, color):
        """
        Pass color changes on to the selected cells
        :return:
        """
        for index in self.selectedIndexes():
            self.model().setData(index, color, )

    def selectionChanged(self, selected, deselected):
        # selected and deselected are deltas. Whatever comes in selected needs to be enabled in the target list,
        # whatever is in deselected needs to be disabled,
        super().selectionChanged(selected, deselected)
        self.model().selection_changed(selected, deselected)


class CenterPanel(QtWidgets.QWidget):
    try_clicked = Signal(list, object)

    """
    Main window central widget
    """
    def __init__(self):
        super().__init__()
        self.main_layout = QtWidgets.QGridLayout(self)
        # self.setLayout(self.main_layout)

        self.device_widget = DeviceListView(self)
        self.target_widget = TargetTableView(self)
        self.effect_widget = QtWidgets.QListView()
        self.color_widget = QtWidgets.QColorDialog()
        self.try_button = QtWidgets.QPushButton('&Try')
        self.apply_button = QtWidgets.QPushButton('&Apply')

        # Hide OK/Cancel buttons on color picker
        self.color_widget.setOption(QtWidgets.QColorDialog.NoButtons, True)
        self.color_widget.currentColorChanged.connect(self.target_widget.color_change)

        self._assemble_panel()

        self.try_button.clicked.connect(self._try_clicked)

    def _assemble_panel(self):
        self.main_layout.addWidget(self.device_widget, 0, 0)
        self.main_layout.addWidget(self.target_widget, 1, 0, 1, 2)
        self.main_layout.addWidget(self.effect_widget, 0, 1)
        self.main_layout.addWidget(self.color_widget, 0, 2, 2, 2)
        self.main_layout.addWidget(self.try_button, 2, 0)
        self.main_layout.addWidget(self.apply_button, 2, 1)

    def _try_clicked(self):
        # Relay Try button click with all selected items
        self.try_clicked.emit(self.effect_widget.selectedIndexes(),
                              self.color_widget.currentColor())

    def set_device_list(self, device_list):
        """
        Attach the model for the device list panel
        :param device_list:
        :return:
        """
        self.device_widget.setModel(device_list)
        self.device_widget.setCurrentIndex(device_list.index(0, 0))

    def set_target_table(self, target_table):
        """
        Attach the model for the target table panel
        :param target_table:
        :return:
        """
        self.target_widget.setModel(target_table)

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
