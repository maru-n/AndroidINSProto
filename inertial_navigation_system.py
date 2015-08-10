#!/usr/bin/env python

from abc import ABCMeta, abstractmethod
import serial
import struct


class INS(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        super(INS, self).__init__()

    @abstractmethod
    def get_quaternion(self):
        pass

    @abstractmethod
    def get_all_sensor_data(self):
        pass


class AndroidINS(INS):

    def get_quaternion(self):
        pass

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

    def get_all_sensor_data(self):
        return self.fetch_all_data()

    def __del__(self):
        try:
            self.__serial.close()
        except:
            pass


class VN100INS(object):
    def get_quaternion(self):
        pass
