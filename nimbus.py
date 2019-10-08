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


class Nimbus(QtWidgets.QMainWindow):
    """
    GUI class for the Asus LED control
    """
    def __init__(self):
        super().__init__()

        self.setGeometry(10, 10, 300, 300)
        self.setWindowTitle('PyAura')
        self.statusBar().showMessage('Ready')


if __name__ == '__main__':
    application = QtWidgets.QApplication(sys.argv)
    aura = Nimbus()

    aura.show()

    sys.exit(application.exec_())
