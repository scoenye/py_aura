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
import hid

from abc import ABC, abstractmethod

import animation.devices.mouse as mouse
import animation.devices.keyboard as keyboard

from animation.effects import Effects
from udev import USBEventListener, NodeResolver


class Device(ABC):
    """
    Base class for Aura USB devices
    """
    VENDOR_ID = 0x0b05
    PRODUCT_ID = 0x0000
    INTERFACE = 0
    EFFECT_MAP = {}

    def __init__(self, bus_location):
        self.bus_location = bus_location
        self.handle = None                  # HID device handle
        self.targets = None

    def _find_path(self):
        # Start of with the list of matching hardware
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

    @abstractmethod
    def effect(self, descriptor):
        """
        Obtain a device specific instance of an effect
        :param descriptor: which effect to create
        :return:
        """


class LEDTarget:
    """
    A targetable LED on a device
    """
    def __init__(self, device, target, name):
        self.device = device
        self.target = target            # Target LED USB report identifier
        self.display_name = name
        self.color_rgb = (0, 0, 0)

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


class GladiusIIMouse(Device):
    """
    Asus RoG Gladius II mouse
    """
    PRODUCT_ID = 0x1845
    INTERFACE = 2

    EFFECT_MAP = {
        Effects.STATIC: mouse.StaticEffectGladius,
        Effects.STROBE: mouse.StrobeEffectGladius,
        Effects.CYCLE: mouse.CycleEffectGladius,
        Effects.RAINBOW: mouse.RainbowEffectGladius
    }

    # Selectable LEDs
    LED_LOGO = 0x00     # Selects the logo LED
    LED_WHEEL = 0x01    # Selects the wheel LED
    LED_BASE = 0x02     # Selects the mouse base
    LED_ALL = 0x03      # Selects all LEDs

    def __init__(self, bus_location):
        super().__init__(bus_location)
        self.targets = [
            LEDTarget(self, GladiusIIMouse.LED_ALL, 'ALL'),
            LEDTarget(self, GladiusIIMouse.LED_LOGO, 'Logo'),
            LEDTarget(self, GladiusIIMouse.LED_WHEEL, 'Wheel'),
            LEDTarget(self, GladiusIIMouse.LED_BASE, 'Base')
        ]

    def effect(self, descriptor):
        return GladiusIIMouse.EFFECT_MAP.get(descriptor)(self)


class ITEKeyboard(Device):
    """
    Asus ITE keyboard (8910)
    """
    PRODUCT_ID = 0x1869

    EFFECT_MAP = {
        Effects.STATIC: keyboard.StaticEffectITE,
        Effects.STROBE: keyboard.StrobeEffectITE,
        Effects.CYCLE: keyboard.CycleEffectITE,
        Effects.RAINBOW: keyboard.RainbowEffectITE
    }

    # Selectable segments
    LED_ALL = 0
    LED_SEGMENT1 = 1
    LED_SEGMENT2 = 2
    LED_SEGMENT3 = 3
    LED_SEGMENT4 = 4
    LED_SEGMENT5 = 5
    LED_SEGMENT6 = 6
    LED_SEGMENT7 = 7

    def __init__(self, bus_location):
        super().__init__(bus_location)
        self.targets = [
            LEDTarget(self, ITEKeyboard.LED_ALL, 'ALL'),
            LEDTarget(self, ITEKeyboard.LED_SEGMENT1, 'Segment 1'),      # The 4 hardware segments
            LEDTarget(self, ITEKeyboard.LED_SEGMENT2, 'Segment 2'),
            LEDTarget(self, ITEKeyboard.LED_SEGMENT3, 'Segment 3'),
            LEDTarget(self, ITEKeyboard.LED_SEGMENT4, 'Segment 4')
        ]

    def effect(self, descriptor):
        return ITEKeyboard.EFFECT_MAP.get(descriptor)(self)


# Supported devices
SUPPORTED_DEVICES = {
    '0b05': {
        '1845': GladiusIIMouse,
        '1869': ITEKeyboard
    }
}


class DeviceList(USBEventListener):
    """
    List of supported devices currently connected to the computer
    """
    def __init__(self):
        self.devices = {}
        self.model_list = []    # dict does not fit in Qt's model concept

    def __len__(self):
        return len(self.model_list)

    def __getitem__(self, item):
        return self.devices[self.model_list[item]]['name']

    def added(self, vendor_id, product_id, bus_num, dev_num, model):
        """
        Handle addition of a new device to the computer
        :param vendor_id: USB vendor ID
        :param product_id: USB product ID
        :param bus_num: bus number the device is connected to
        :param dev_num: device number on the bus
        :param model: human readable (YMMV) description of the device
        :return:
        """
        # vendor_id/product_id are used to figure out if the device is supported
        # bus_num/dev_num will be the key in the device list.
        if vendor_id in SUPPORTED_DEVICES:
            if product_id in SUPPORTED_DEVICES[vendor_id]:
                key = (bus_num, dev_num)
                self.devices[key] = {'name': model,
                                     'instance': SUPPORTED_DEVICES[vendor_id][product_id](key)}
                self.model_list.append(key)     # Get around Qt model limitations

    def removed(self, bus_num, dev_num):
        """
        Hamdle unplugging of a device
        :param bus_num: bus number the device was connected to
        :param dev_num: device number on the bus
        :return:
        """
        if (bus_num, dev_num) in self.devices:
            key = (bus_num, dev_num)
            del self.devices[key]
            self.model_list.remove(key)

    def instances(self, selection):
        """
        Convert model selection into device instances
        :param selection: list of selected device indices
        :return: list of device instances corresponding to selection
        """
        device_list = []

        for item in selection:      # Index into model_list
            real_key = self.model_list[item]
            device_list.append(self.devices[real_key]['instance'])

        return device_list


class TargetLEDTable:
    """
    Aggregates all LEDs on all devices
    :return:
    """
    def __init__(self):
        self.targets = [
            [
                LEDTarget(self, GladiusIIMouse.LED_ALL, 'ALL'),
                LEDTarget(self, GladiusIIMouse.LED_LOGO, 'Logo'),
                LEDTarget(self, GladiusIIMouse.LED_WHEEL, 'Wheel'),
                LEDTarget(self, GladiusIIMouse.LED_BASE, 'Base')],
            [
                LEDTarget(self, ITEKeyboard.LED_ALL, 'ALL'),
                LEDTarget(self, ITEKeyboard.LED_SEGMENT1, 'Segment 1'),  # The 4 hardware segments
                LEDTarget(self, ITEKeyboard.LED_SEGMENT2, 'Segment 2'),
                LEDTarget(self, ITEKeyboard.LED_SEGMENT3, 'Segment 3'),
                LEDTarget(self, ITEKeyboard.LED_SEGMENT4, 'Segment 4')]
        ]

    def __len__(self):
        """
        Return the length of the longest list of targets
        :return:
        """
        return max([len(target_list) for target_list in self.targets])

    def __getitem__(self, item):
        """
        Produces the regular data items for the Qt view
        :param item: index of the
        :return:
        """
        return self.targets[item]


class MetaDevice:
    """
    Apply an effect to multiple devices
    """
    def __init__(self, devices, effect, color):
        """
        :param devices: list of device instances to apply the effect to
        :param effect: effect to apply to the devices
        :param color: initial color selection for the effect
        """
        self.devices = devices
        self.effect = effect
        self.color = color

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

    def try_out(self):
        """
        Execute the effect but do not issue an "apply" command
        :return:
        """
        active_effects = [device.effect(self.effect) for device in self.devices]

        for effect in active_effects:
            effect.color(self.color[0], self.color[1], self.color[2])
            effect.start()
