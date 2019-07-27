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

report = bytearray(64)
report[0] = 0x51
report[1] = 0x28
report[5] = 0x04
report[6] = 0xff
report[7] = 0x00
report[8] = 0x00

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

    report[2] = 0x00    # Controls logo
#    xferred = handle.interruptWrite(0x04, report, 64)
#    print('write 0: ', xferred)

    report[2] = 0x01    # Controls wheel
    xferred = handle.interruptWrite(0x04, report, 64)
#    print('write 1: ', xferred)

    report[2] = 0x02    # Controls bottom LED track
#    xferred = handle.interruptWrite(0x04, report, 64)
#    print('write 2: ', xferred)

#    xferred = handle.interruptRead(0x83, 64)
#    print('read 0: ', xferred)

#    xferred = handle.interruptRead(0x83, 64)
#    print('read 1: ', xferred)

#    xferred = handle.interruptRead(0x83, 64)
#    print('read 2: ', xferred)


    handle.releaseInterface(2)

    if kernel_attached:
        handle.attachKernelDriver(2)


