#!/usr/bin/env python

import serial
import struct


class DataReceiver(object):
    """docstring for DataReceiver"""
    def __init__(self):
        super(DataReceiver, self).__init__()

    def set_serial_settings(self, serial_device, baudrate=115200, timeout=0.1):
        self.__serial = serial.Serial(serial_device, baudrate, timeout=timeout)

    def fetch_all_data(self):
        self.__serial.write([1])
        data_num = 12*3
        bytes = self.__serial.read(data_num)
        if len(bytes) == data_num:
            return struct.unpack('>fffffffff', bytes)
        else:
            self.__serial.flush()
            Exception("No data received.")

    def __del__(self):
        try:
            self.__serial.close()
        except:
            pass
