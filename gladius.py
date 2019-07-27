"""
    gladius
    A demo program to change the Asus RoG Gladius II mouse LED colors.

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

import usb1

from report import GladiusIIReport

report = GladiusIIReport()

# find our device
with usb1.USBContext() as context:
    handle = context.openByVendorIDAndProductID(
        0x0b05,
        0x1845,
        skip_on_error=True,
    )

    # was it found?
    if handle is None:
        raise ValueError('Device not found')

    kernel_attached = handle.kernelDriverActive(2)
    if kernel_attached:
        handle.detachKernelDriver(2)

    handle.claimInterface(2)

    report.color(0x20, 0x00, 0x20)      # Deep Purple

    report.target(GladiusIIReport.LED_LOGO)
    xferred = report.send(handle)
    print('write 0: ', xferred)

    report.target(GladiusIIReport.LED_WHEEL)
    report.send(handle)
    print('write 1: ', xferred)

    report.target(GladiusIIReport.LED_BASE)
    xferred = report.send(handle)
    print('write 2: ', xferred)

#    xferred = handle.interruptRead(0x83, 64)
#    print('read 0: ', xferred)

#    xferred = handle.interruptRead(0x83, 64)
#    print('read 1: ', xferred)

#    xferred = handle.interruptRead(0x83, 64)
#    print('read 2: ', xferred)

    handle.releaseInterface(2)

    if kernel_attached:
        handle.attachKernelDriver(2)


