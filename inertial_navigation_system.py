#!/usr/bin/env python

from abc import ABCMeta, abstractmethod
import serial
import struct


class INS(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        super(INS, self).__init__()

    def __del__(self):
        self.stop()

    def setup_serial(self, serial_device, baudrate=115200, timeout=0.1):
        self.serial = serial.Serial(serial_device, baudrate, timeout=timeout)

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def get_quaternion(self):
        pass

    @abstractmethod
    def get_all_sensor_data(self):
        pass


class AndroidINS(INS):
    def __init__(self):
        super(AndroidINS, self).__init__()

    def start(self):
        pass

    def stop(self):
        try:
            self.serial.close()
        except:
            pass

    def get_all_sensor_data(self):
        self.serial.write([1])
        data_num = 12*3
        bytes = self.serial.read(data_num)
        if len(bytes) == data_num:
            return struct.unpack('>fffffffff', bytes)
        else:
            self.serial.flush()
            Exception("No data received.")


class VN100INS(object):
    def __init__(self):
        super(VN100INS, self).__init__()

    def get_quaternion(self):
        pass
