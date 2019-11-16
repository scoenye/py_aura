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

    def __init__(self, bus_location, model):
        self.bus_location = bus_location    # To link USB HID and udev world views
        self.model = model
        self.handle = None                  # HID device handle
        self.targets = None
        self.is_selected = False

    def __repr__(self):
        return self.model

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


class GladiusIIMouse(Device):
    """
    Asus RoG Gladius II mouse
    """
    PRODUCT_ID = 0x1845
    INTERFACE = 2

    EFFECT_MAP = {
        Effects.STATIC: mouse.StaticEffectHW,
        Effects.BREATHE: mouse.BreatheEffectHW,
        Effects.STROBE: mouse.StrobeEffectGladius,
        Effects.CYCLE: mouse.CycleEffectGladius,
        Effects.RAINBOW: mouse.RainbowEffectGladius
    }

    # Selectable LEDs
    LED_LOGO = 0x00     # Selects the logo LED
    LED_WHEEL = 0x01    # Selects the wheel LED
    LED_BASE = 0x02     # Selects the mouse base
    LED_ALL = 0x03      # Selects all LEDs

    def __init__(self, bus_location, model):
        super().__init__(bus_location, model)
        self.targets = [
            LEDTarget(self, GladiusIIMouse.LED_ALL, 'ALL'),
            LEDTarget(self, GladiusIIMouse.LED_LOGO, 'Logo'),
            LEDTarget(self, GladiusIIMouse.LED_WHEEL, 'Wheel'),
            LEDTarget(self, GladiusIIMouse.LED_BASE, 'Base')
        ]

    def effect(self, descriptor):
        return GladiusIIMouse.EFFECT_MAP.get(descriptor)(self)

    def selected_targets(self):
        """
        Return the list of selected targets for the device. Return the ALL target if no selection was made.
        :return: list of selected targets
        """
        base_list = super().selected_targets()          # The list of actually selected targets, if any.
        return base_list or [self.targets[GladiusIIMouse.LED_ALL]]


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

    def __init__(self, bus_location, model):
        super().__init__(bus_location, model)
        self.targets = [
            LEDTarget(self, ITEKeyboard.LED_ALL, 'ALL'),
            LEDTarget(self, ITEKeyboard.LED_SEGMENT1, 'Segment 1'),      # The 4 hardware segments
            LEDTarget(self, ITEKeyboard.LED_SEGMENT2, 'Segment 2'),
            LEDTarget(self, ITEKeyboard.LED_SEGMENT3, 'Segment 3'),
            LEDTarget(self, ITEKeyboard.LED_SEGMENT4, 'Segment 4')
            # LEDTarget(self, ITEKeyboard.LED_SEGMENT5, 'SW Segment 5'),      # The extra undefined segments
            # LEDTarget(self, ITEKeyboard.LED_SEGMENT6, 'SW Segment 6'),      # used by the parallel report
            # LEDTarget(self, ITEKeyboard.LED_SEGMENT7, 'SW Segment 7')
        ]

    def effect(self, descriptor):
        return ITEKeyboard.EFFECT_MAP.get(descriptor)(self)

    def selected_targets(self):
        """
        Return the list of selected targets for the device. Return the ALL target if no selection was made.
        :return: list of selected targets
        """
        base_list = super().selected_targets()          # The list of actually selected targets, if any.
        return base_list or [self.targets[ITEKeyboard.LED_ALL]]

    def parallel_targets(self):
        """
        Return the list of selected targets suitable for use by the parallel report(s). All targets are returned
        if no selection was made.
        :return: list of selected targets
        """
        base_list = super().selected_targets()

        if not base_list:       # No selection: use the colors as defined for the synthetic all target components
            base_list = [self.targets[ITEKeyboard.LED_SEGMENT1], self.targets[ITEKeyboard.LED_SEGMENT2],
                         self.targets[ITEKeyboard.LED_SEGMENT3], self.targets[ITEKeyboard.LED_SEGMENT4]]
        elif base_list == [self.targets[ITEKeyboard.LED_ALL]]:
            base_list = [self.targets[ITEKeyboard.LED_SEGMENT1], self.targets[ITEKeyboard.LED_SEGMENT2],
                         self.targets[ITEKeyboard.LED_SEGMENT3], self.targets[ITEKeyboard.LED_SEGMENT4]]

            # As there is no real ALL target (?), copy its color to the components
            for target in base_list:
                target.change_color(self.targets[ITEKeyboard.LED_ALL].color())  # TODO: tell the view?

        return base_list


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
        self.device_targets = TargetLEDTable(self)

    def __len__(self):
        return len(self.model_list)

    def __getitem__(self, item):
        return self.devices[self.model_list[item]]

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
                self.devices[key] = SUPPORTED_DEVICES[vendor_id][product_id](key, model)
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

    def select(self, index):
        """
        Tell a device it has been selected on-screen
        :param index: selected device index
        :return:
        """
        self[index].select()

    def deselect(self, index):
        """
        Tell a device it has been removed from selection
        :param index: deselected device index
        :return:
        """
        self[index].deselect()

    def selected(self):
        """
        Generate a list of the currently selected devices
        :return: list of selected devices
        """
        device_list = []

        for device in self.devices.values():  # Index into model_list
            if device.selected():
                device_list.append(device)

        return device_list

    def target_table(self):
        """
        Return the TargetLEDTable instance responsible for communication about the targets available on the devices
        in this DevjceList.
        :return: TargetLEDTable instance
        """
        return self.device_targets


class TargetLEDTable:
    """
    Aggregates all LEDs on all devices
    :return:
    """
    def __init__(self, device_list):
        self.device_list = device_list

    def __len__(self):
        """
        Return the length of the longest list of targets
        :return:
        """
        return max([len(device.show_targets()) for device in self.device_list])

    def __getitem__(self, item):
        """
        Produces the regular data items for the Qt view
        :param item: index of the
        :return:
        """
        return self.device_list[item].show_targets()

    def select(self, device_index, target_index):
        """
        Tell a target it has been selected on-screen
        :param device_index: device index of the selected target
        :param target_index: selected target index
        :return:
        """
        try:
            self[device_index][target_index].select()
        except IndexError:          # Non-existing target selected
            pass

    def deselect(self, device, target):
        """
        Tell a target it has been removed from selection
        :param device: device index of the deselected target
        :param target: deselected target index
        :return:
        """
        try:
            self[device][target].deselect()
        except IndexError:          # Non-existing target selected
            pass

    def device_count(self):
        """
        Return how many devices this container holds
        :return:
        """
        return len(self.device_list)

    def device_name(self, section):
        """
        Return the device name for a set of targets
        :return:
        """
        return str(self.device_list[section])


class MetaDevice:
    """
    Apply an effect to multiple devices
    """
    def __init__(self, devices, effect, color):
        """
        :param devices: list of device instances to apply the effect to
        :param effect: descriptor of the effect to apply to the devices
        :param color: initial color selection for the effect
        """
        self.devices = devices
        self.effect = effect
        self.color = color
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

    def try_out(self):
        """
        Execute the effect but do not issue an "apply" command
        :return:
        """
        self.active_effects = [device.effect(self.effect) for device in self.devices]

        for effect in self.active_effects:
            effect.color(self.color[0], self.color[1], self.color[2])
            effect.start()

    def stop(self):
        """
        Signal all running effects it is time to stop
        :return:
        """
        for effect in self.active_effects:
            effect.stop()
