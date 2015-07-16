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
        msg = ''
        msg += 'accel(x:% 9.5f y:% 9.5f z:% 9.5f)  ' % (ax, ay, az)
        msg += 'gyro(x:% 9.5f y:% 9.5f z:% 9.5f)  ' % (gx, gy, gz)
        msg += 'mag(x:% 10.5f y:% 10.5f z:% 10.5f)' % (mx, my, mz)
    else:
        msg = "no data available."
    sys.stdout.write('\r\033[K' + msg)
    sys.stdout.flush()


ser.close()
