"""
    Aura USB
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

import sys

from PySide2 import QtWidgets

from device import DeviceList

from animation.effects import EffectList
from udev import USBEnumerator
from ui import panels, models


class Nimbus(QtWidgets.QMainWindow):
    """
    GUI class for the Asus LED control
    """
    def __init__(self):
        super().__init__()

        self.device_list = DeviceList()
        self._populate_devices()

        self.effect_list = EffectList()

        self.device_model = models.DeviceListModel(self.device_list)
        self.effect_model = models.EffectListModel(self.effect_list)

        self.center_panel = panels.CenterPanel()

        self.center_panel.set_device_list(self.device_model)
        self.center_panel.set_effect_list(self.effect_model)

        self.center_panel.add_try_listener(self.try_clicked)

        self.setGeometry(10, 10, 300, 300)
        self.setWindowTitle('Nimbus')
        self.statusBar().showMessage('Ready')
        self.setCentralWidget(self.center_panel)

    def _populate_devices(self):
        # Grab the currently connected USB devices
        enum = USBEnumerator()

        enum.add_listener(self.device_list)
        enum.enumerate()

    def try_clicked(self, selected_devices, selected_effect):
        """
        Handle a click on the try button
        :param selected_devices: List of QModelIndex instances representing the selected devices
        :param selected_effect: List with the QModelIndex of the selected effect.
        :return:
        """
        device_keys = [index.row() for index in selected_devices]
        effect_keys = [index.row() for index in selected_effect]

        devices = self.device_list.instances(device_keys)
        effect = self.effect_list.instance(effect_keys)



if __name__ == '__main__':
    application = QtWidgets.QApplication(sys.argv)
    nimbus = Nimbus()

    nimbus.show()

    sys.exit(application.exec_())
