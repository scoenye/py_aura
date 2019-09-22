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
import threading


class Effect:
    """
    Base class for lighting effects
    """
    def __init__(self):
        self.red = None
        self.green = None
        self.blue = None

    def color(self, red, green, blue):
        """
        Set the color for the effect
        :param red: Red value, 0 - 255
        :param green: Green value, 0 - 255
        :param blue: Blue value, 0 - 255
        :return:
        """
        self.red = red
        self.green = green
        self.blue = blue

    def start(self, device, targets=None):
        """
        Start execution of the effect
        :param device: Device to apply the effect to.
        :param targets: list of LEDs to change color of, None to change all LEDs
        :return:
        """
        pass


class RunnableEffect(Effect):
    """
    Threaded lighting effect
    """
    def __init__(self):
        super().__init__()
        self.device = None
        self.targets = []
        self.thread = threading.Thread(target=self._runnable)
        self.keep_running = True

    def _runnable(self):
        # Core of the strobe effect thread
        pass

    def start(self, device, targets=None):
        """
        Start the execution of the effect as a separate thread.
        :param device: Device to apply the effect to.
        :param targets: list of LEDs to change color of, None to change all LEDs
        :return:
        """
        self.device = device
        self.targets = targets
        self.thread.start()

    def stop(self):
        """
        Signal the thread to stop running.
        :return:
        """
        self.keep_running = False
        self.thread.join()
