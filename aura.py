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

from device.core import MetaDevice
from device.containers import DeviceList, TargetLEDTable

from animation.effects import EffectList
from udev import USBEnumerator, USBMonitor
from ui import panels, models


class Aura(QtWidgets.QMainWindow):
    """
    GUI class for the ASUS LED control
    """
    def __init__(self):
        super().__init__()

        self.meta_device = None

        self.device_list = DeviceList()
        self._populate_devices()
        self.usb_monitor = USBMonitor()
        self.usb_monitor.add_listener(self.device_list)
        self.usb_monitor.start()

        self.effect_list = EffectList()

        self.device_model = models.DeviceListModel(self.device_list)
        self.target_model = models.TargetTableModel(self.device_list, self.device_list.target_table())
        self.effect_model = models.EffectListModel(self.effect_list)

        self.center_panel = panels.CenterPanel()

        self.center_panel.set_device_list(self.device_model)
        self.center_panel.set_target_table(self.target_model)
        self.center_panel.set_effect_list(self.effect_model)

        self.center_panel.add_try_listener(self.try_clicked)
        self.center_panel.add_apply_listener(self.apply_clicked)
        self.center_panel.add_stop_listener(self.stop_clicked)

        self.setGeometry(10, 10, 1000, 300)
        self.setWindowTitle('Nimbus')
        self.statusBar().showMessage('Ready')
        self.setCentralWidget(self.center_panel)

    def _populate_devices(self):
        # Grab the currently connected USB devices
        enum = USBEnumerator()

        enum.add_listener(self.device_list)
        enum.enumerate()

    def try_clicked(self, selected_effect, use_hw):
        """
        Handle a click on the try button
        :param selected_effect: List with the QModelIndex of the selected effect.
        :param use_hw: use hardware effects if true, software effects if false
        :return:
        """
        effect_keys = [index.row() for index in selected_effect]

        devices = self.device_list.selected()
        effect = self.effect_list.instance(effect_keys)

        if self.meta_device:
            self.meta_device.stop()
            self.meta_device.close()

        self.meta_device = MetaDevice(devices, effect)
        self.meta_device.open()
        self.meta_device.try_out(use_hw)

    def apply_clicked(self, selected_effect):
        """
        Handle a click on the apply button.
        :param selected_effect: List with the QModelIndex of the selected effect.
        :return:
        """
        effect_keys = [index.row() for index in selected_effect]

        devices = self.device_list.selected()
        effect = self.effect_list.instance(effect_keys)

        if self.meta_device:
            self.meta_device.stop()
            self.meta_device.close()

        self.meta_device = MetaDevice(devices, effect)
        self.meta_device.open()
        self.meta_device.apply()
        self.meta_device.close()

    def stop_clicked(self):
        """
        Handle a click on the stop button
        :return:
        """
        if self.meta_device:
            self.meta_device.stop()
            self.meta_device.close()

    def color_changed(self, color):
        """
        Handle a change in color requested by the user
        :param color: QColor instance with the color to change to
        :return:
        """
        self.effect_model.change_color(color)

    def closeEvent(self, event):
        """
        Clean up on window closure
        :param event:
        :return:
        """
        self.usb_monitor.stop()
        event.accept()


if __name__ == '__main__':
    application = QtWidgets.QApplication(sys.argv)
    aura = Aura()

    aura.show()

    sys.exit(application.exec_())
