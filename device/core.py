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
import hid

from abc import ABC

from animation.effects import NullEffect, Implementation
from udev import NodeResolver


class Device(ABC):
    """
    Base class for Aura USB devices
    """
    VENDOR_ID = 0x0b05
    PRODUCT_ID = 0x0000
    INTERFACE = 0
    EFFECT_MAP = {}

    def __init__(self, bus_location, model):
        self.bus_location = bus_location    # To link USB HID and udev world views
        self.model = model
        self.handle = None                  # HID device handle
        self.targets = None
        self.is_selected = False

    def __repr__(self):
        return self.model

    def _find_path(self):
        # Start off with the list of matching hardware
        device_list = hid.enumerate(self.VENDOR_ID, self.PRODUCT_ID)

        for device in device_list:
            # See if the device is plugged in to the correct port
            if NodeResolver.bus_location(device['path']) == self.bus_location:
                if device['interface_number'] == self.INTERFACE:
                    return device['path']

    def open(self):
        """
        Ready the device for use
        :return:
        """
        path = self._find_path()

        try:
            self.handle = hid.Device(path=path)
        except Exception:
            raise ValueError('Device not found:', self.VENDOR_ID, self.PRODUCT_ID, self.bus_location)

    def close(self):
        """
        Release the device
        :return:
        """
        self.handle.close()

    def write_interrupt(self, report):
        """
        Accept a report to send to the device's Aura endpoint
        :param report: report to send to the device
        :return: number of bytes transferred to the device
        """
        return report.send(self.handle)

    def read_interrupt(self, size, timeout=None):
        """
        Request a return report from the device's Aura endpoint
        :param size: amount of data requested
        :param timeout: milliseconds to wait before giving up
        :return: data transmitted by the device
        """
        return self.handle.read(size, timeout)

    def select(self):
        """
        Mark the device as selected
        :return:
        """
        self.is_selected = True

    def deselect(self):
        """
        Forget the device was selected
        :return:
        """
        self.is_selected = False

    def selected(self):
        """
        :return: device selection status
        """
        return self.is_selected

    def show_targets(self):
        """
        Return the collection of the device's targets for display
        :return: list of LEDTarget objects
        """
        return self.targets

    def selected_targets(self):
        """
        Return the list of selected targets for the device.
        :return: list of selected targets
        """
        return [target for target in self.targets if target.selected()]

    def effect(self, descriptor, implementation):
        """
        Obtain a device specific instance of an effect. A "do nothing" effect is returned if the device does not
        support the requested effect implementation.
        :param descriptor: which effect to create
        :param implementation: whether to create a hardware or software effect.
        :return:
        """
        container = self.EFFECT_MAP.get(descriptor)

        if container:  # Requested effect may not be supported at all
            effect_class = container.effect(implementation)

            if effect_class:
                return effect_class(self)

        return NullEffect(self)


class LEDTarget:
    """
    A targetable LED on a device
    """
    def __init__(self, device, target, name):
        self.device = device
        self.target = target            # Target LED USB report identifier
        self.display_name = name
        self.color_rgb = (0, 0, 0)
        self.is_selected = False

    def name(self):
        """
        :return: The display name of the target LED
        """
        return self.display_name

    def color(self):
        """
        Return the current color of the target
        :return:
        """
        return self.color_rgb

    def change_color(self, rgb):
        """
        Set the color for the LED
        :param rgb:
        :return:
        """
        self.color_rgb = rgb
        return True

    def select(self):
        """
        Mark the device as selected
        :return:
        """
        self.is_selected = True

    def deselect(self):
        """
        Forget the device was selected
        :return:
        """
        self.is_selected = False

    def selected(self):
        """
        :return: target selection status
        """
        return self.is_selected

    def target_segment(self):
        """
        :return: the USB report identifier of the target
        """
        return self.target


class MetaDevice:
    """
    Apply an effect to multiple devices
    """
    def __init__(self, devices, effect):
        """
        :param devices: list of device instances to apply the effect to
        :param effect: descriptor of the effect to apply to the devices
        """
        self.devices = devices
        self.effect = effect
        self.active_effects = None

    def open(self):
        """
        Open all individual devices
        :return:
        """
        for device in self.devices:
            device.open()

    def close(self):
        """
        Close all individual devices
        :return:
        """
        for device in self.devices:
            device.close()

    def try_out(self, use_hw):
        """
        Execute the effect but do not issue an "apply" command
        :param use_hw: use hardware implementation if true, software otherwise.
        :return:
        """
        if use_hw:
            implementation = Implementation.HARDWARE
        else:
            implementation = Implementation.SOFTWARE

        self.active_effects = [device.effect(self.effect, implementation) for device in self.devices]

        for effect in self.active_effects:
            effect.start()

    def apply(self):
        """
        Make the current effect permanent if supported by the underlying hardware.
        :return:
        """
        self.active_effects = [device.effect(self.effect, Implementation.HARDWARE) for device in self.devices]

        for effect in self.active_effects:
            effect.apply()

    def stop(self):
        """
        Signal all running effects it is time to stop
        :return:
        """
        for effect in self.active_effects:
            effect.stop()
