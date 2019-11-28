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

import sys
import time

from PySide2 import QtWidgets

from device import DeviceList, TargetLEDTable, MetaDevice

from animation.effects import EffectList
from udev import USBEnumerator
from ui import panels, models


class Aura(QtWidgets.QMainWindow):
    """
    GUI class for the ASUS LED control
    """
    def __init__(self):
        super().__init__()

        self.device_list = DeviceList()
        self._populate_devices()

        self.effect_list = EffectList()

        self.device_model = models.DeviceListModel(self.device_list)
        self.target_model = models.TargetTableModel(self.device_list.target_table())
        self.effect_model = models.EffectListModel(self.effect_list)

        self.center_panel = panels.CenterPanel()

        self.center_panel.set_device_list(self.device_model)
        self.center_panel.set_target_table(self.target_model)
        self.center_panel.set_effect_list(self.effect_model)

        self.center_panel.add_try_listener(self.try_clicked)
        self.center_panel.add_apply_listener(self.apply_clicked)

        self.setGeometry(10, 10, 1000, 300)
        self.setWindowTitle('Nimbus')
        self.statusBar().showMessage('Ready')
        self.setCentralWidget(self.center_panel)

    def _populate_devices(self):
        # Grab the currently connected USB devices
        enum = USBEnumerator()

        enum.add_listener(self.device_list)
        enum.enumerate()

    def try_clicked(self, selected_effect, color):
        """
        Handle a click on the try button
        :param selected_effect: List with the QModelIndex of the selected effect.
        :param color: selected QColor for the effect
        :return:
        """
        effect_keys = [index.row() for index in selected_effect]

        devices = self.device_list.selected()
        effect = self.effect_list.instance(effect_keys)

        meta_device = MetaDevice(devices, effect, (color.red(), color.green(), color.blue()))
        meta_device.open()
        meta_device.try_out()
        meta_device.stop()
        meta_device.close()

    def apply_clicked(self, selected_effect):
        """
        Handle a click on the apply button.
        :param selected_effect: List with the QModelIndex of the selected effect.
        :return:
        """
        effect_keys = [index.row() for index in selected_effect]

        devices = self.device_list.selected()
        effect = self.effect_list.instance(effect_keys)

        meta_device = MetaDevice(devices, effect, (0, 0, 0))
        meta_device.open()
        meta_device.apply()
        meta_device.close()

    def color_changed(self, color):
        """
        Handle a change in color requested by the user
        :param color: QColor instance with the color to change to
        :return:
        """
        self.effect_model.change_color(color)


if __name__ == '__main__':
    application = QtWidgets.QApplication(sys.argv)
    aura = Aura()

    aura.show()

    sys.exit(application.exec_())