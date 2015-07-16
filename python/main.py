#!/usr/bin/env python

import serial
import struct
import sys

serial_device = sys.argv[1]
baudrate = 115200
ser = serial.Serial(serial_device, baudrate, timeout=0.1)

while True:
    ser.write([1])
    data_num = 12*3
    bytes = ser.read(data_num)
    if len(bytes) == data_num:
        ax, ay, az, gx, gy, gz, mx, my, mz = struct.unpack('>fffffffff', bytes)
        print('accel(x:%f y:%f z:%f) ' % (ax, ay, az), end="")
        print('gyro(x:%f y:%f z:%f) ' % (gx, gy, gz), end="")
        print('mag(x:%f y:%f z:%f)' % (mx, my, mz))
    else:
        print("no data available.")


ser.close()
