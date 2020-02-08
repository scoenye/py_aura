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
from udev import USBEventListener

from device.keyboard import ITEKeyboard
from device.mouse import GladiusIIMouse


# At this time, it is not possible to use the PRODUCT_ID fields in the concrete devices as keys in the supported
# devices dict: the udev enumerator returns hex strings, the HID path discovery in the devices needs the ID
# in integer form.
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
        self.update_listeners = []

    def __len__(self):
        return len(self.model_list)

    def __getitem__(self, item):
        return self.devices[self.model_list[item]]

    def add_update_listener(self, listener):
        """
        Add a listener interested in receiving updates about external changes to the device list.
        :param listener: ListUpdateListener instance to add to the collection interested in update notifications.
        :return:
        """
        self.update_listeners.append(listener)

    def remove_update_listener(self, listener):
        """
        Remove a listener from the external changes update list.
        :param listener: ListUpdateListener instance to remove from the collection of update listeners.
        :return:
        """
        self.update_listeners.remove(listener)

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
                self.model_list.append(key)                 # Get around Qt model limitations
                for listener in self.update_listeners:      # Signal models their data changed.
                    listener.insert(len(self.model_list))

    def removed(self, bus_num, dev_num):
        """
        Hamdle unplugging of a device
        :param bus_num: bus number the device was connected to
        :param dev_num: device number on the bus
        :return:
        """
        key = (bus_num, dev_num)

        if key in self.devices:
            model_index = self.model_list.index(key)

            self.device_targets.remove(model_index)     # TODO: make this a real ListUpdateListener
            for listener in self.update_listeners:
                listener.remove(model_index)

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

    def target_count(self):
        """
        :return: the length of the longest list of targets
        """
        return max([device.target_count() for device in self.devices.values()])

    def target_name(self, device_index, target_index):
        """
        :param device_index: Index of the device in the model list
        :param target_index: Index of he target on the requested device
        :return: the name of the requested target
        """
        return self[device_index].target_name(target_index)

    def target_color(self, device_index, target_index):
        """
        :param device_index: Index of the device in the model list
        :param target_index: Index of he target on the requested device
        :return: the current color of the requested target
        """
        return self[device_index].target_color(target_index)

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
    """
    def __init__(self, device_list):
        self.device_list = device_list
        self.update_listeners = []
        # TODO: make TLT an update_listener (class hierarchy needs sorting out as UL is now tied to Qt.)

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

    def add_update_listener(self, listener):
        """
        Add a listener interested in receiving updates about external changes to the device list.
        :param listener: ListUpdateListener instance to add to the collection interested in update notifications.
        :return:
        """
        self.update_listeners.append(listener)

    def remove_update_listener(self, listener):
        """
        Remove a listener from the external changes update list.
        :param listener: ListUpdateListener instance to remove from the collection of update listeners.
        :return:
        """
        self.update_listeners.remove(listener)

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

    def remove(self, index):
        """
        Remove the targets for the device at the specified index from the table
        :param index:
        :return:
        """
        for listener in self.update_listeners:
            listener.remove(index)