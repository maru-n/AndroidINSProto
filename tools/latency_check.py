#!/usr/bin/env python

import serial
import struct
import sys
import time

serial_device = sys.argv[1]
baudrate = 115200
ser = serial.Serial(serial_device, baudrate, timeout=0.1)

file = open(sys.argv[2], "w")

while True:
    ser.write([1])
    data_num = 12*3
    start = time.time()
    bytes = ser.read(data_num)
    elapsed_time = time.time() - start
    if len(bytes) == data_num:
        file.write(str(elapsed_time)+"\n")
        ax, ay, az, gx, gy, gz, mx, my, mz = struct.unpack('>fffffffff', bytes)
        print('accel(x:%f y:%f z:%f) ' % (ax, ay, az), end="")
        print('gyro(x:%f y:%f z:%f) ' % (gx, gy, gz), end="")
        print('mag(x:%f y:%f z:%f)' % (mx, my, mz))
    else:
        print("no data available.")


ser.close()
