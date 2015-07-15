#!/usr/bin/env python

import serial
import struct
import sys

serial_device = sys.argv[1]
baudrate = 115200
ser = serial.Serial(serial_device, baudrate)

while True:
    data_num = 12
    bytes = ser.read(data_num)
    if len(bytes) != data_num:
        Exception("Couldn't read all serial datas.")
    x, y, z = struct.unpack('>fff', bytes)
    print('x:%f y:%f z:%f' % (x, y, z))

ser.close()
