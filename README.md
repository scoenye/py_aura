# PyAura

A tool to control the LEDs of USB attached ASUS HID peripherals from Linux.

## Prerequisites
```
python 3.7
libhidapi-hidraw0
```
### Python packages
```
hid
pyside2
pyudev
```
## Getting Started

The hid package uses libhidapi. This library in turn can use libusb or hidraw to communicate to the peripherals. libhidapi must use the hidraw backend. libusb is not suitable as it cannot talk to a device if the kernel driver is already attached.

### Hardware/software effects

Hardware effects are built into a device. The set of built-in effects may differ across device types and models. Software effects consist of a continuous stream of color change instructions sent to a device. Both effect types have distinct capabilities and limitations.

Software effects generally mimic hardware effects. It is the mechanism used by ASUS's AuraSync to achieve synchronization across devices as timing differences will eventually lead hardware effects to drift apart.

Some hardware effects have finer grained control over device LEDs than is available to software based effects.

The application needs to remain running to continue a software effect. It can be closed after a hardware effect.

## Running

`python aura.py`

## Operation

The interface has 4 main selection controls (device list, effect list, LED target list, color dialog) and the effect execution buttons.

### Effect list
The list of all effects available.

Hardware selection checkbox: when checked, the hardware implementation of the selected effect will be invoked, if available.

### Device list
The device list shows all supported devices plugged into the computer. Multiple devices can be selected simultaneously. The device list reacts in real-time to device plug/unplug events.

### LED target list
The combined collection of addressable LEDs on all available devices. The selected effect will be applied to all LED targets selected when the Try/Apply button is clicked.

### Color selection dialog
A change to any of the color selection methods will be passed on to the currently selected target LEDs.

Limitation inherited from Qt: the color dialog only sends signals on color changes. To apply the same color to another selection of target LEDs, first pick an arbitrary color, then the desired color.

### Try button
The Try button will execute the chosen effect on all selected devices and LED targets. When the hardware button is checked, the hardware implementation will be used, if supported by the device.

### Apply button
The Apply button instructs the selected devices to make the effect permanent. Not all devices support this and only hardware effects can be made permanent.

### Stop button
Halts the currently running software effect.

## Supported peripherals
py_aura was developed on a RoG Strix Scar/GL703GE laptop. It currently supports the Gladius II mouse and the GL703GE keyboard.

### Gladius II mouse
[VID:PID 0x0b05:0x1845]
Hardware effects cannot be permanently applied. Any effect will be lost when the computer is shut down or the mouse is unplugged and the mouse will revert to the rainbow effect.

### ITE Keyboard
[VID:PID 0x0b05:0x1869]
Hardware based effects can be applied permanently.

## Authors

* **Sven Coenye** - [scoenye](https://github.com/scoenye)

## License

This project is licensed under the GPLv3 License - see the [LICENSE.txt](LICENSE.txt) file for details

