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
    def __init__(self, serial_device_name, serial_baudrate=115200, serial_timeout=0.1):
        super(AndroidINS, self).__init__()
        self._serial_device_name = serial_device_name
        self._serial_baudrate = serial_baudrate
        self._serial_timeout = serial_timeout

    def start(self):
        self.__serial = serial.Serial(self._serial_device_name,
                                      self._serial_baudrate,
                                      timeout=self._serial_timeout)

    def stop(self):
        try:
            self.__serial.close()
        except:
            pass

    def get_quaternion(self):
        # Dummy data!!
        return (0., 0., 0., 0.)

    def get_all_sensor_data(self):
        self.__serial.write([1])
        data_num = 12*3
        bytes = self.__serial.read(data_num)
        if len(bytes) == data_num:
            return struct.unpack('>fffffffff', bytes)
        else:
            self.__serial.flush()
            Exception("No data received.")

from vectornav import *

class VN100INS(INS):
    def __init__(self, serial_device_name):
        super(VN100INS, self).__init__()
        self._serial_device_name = serial_device_name
        self.__latest_quaternion = (0, 0, 0, 0)
        self.__latest_acceleration = (0, 0, 0)
        self.__latest_angular_rate = (0, 0, 0)
        self.__latest_magnetic = (0, 0, 0)

    def start(self):
        self.vn100 = Vn100()
        err_code = vn100_connect(self.vn100, self._serial_device_name, 115200)
        if err_code != VNERR_NO_ERROR:
            raise Exception('Error code: %d' % err_code)
        err_code = vn100_setAsynchronousDataOutputType(self.vn100, VNASYNC_OFF, True)
        if err_code != VNERR_NO_ERROR:
            raise Exception('Error code: %d' % err_code)
        err_code = vn100_setBinaryOutput1Configuration(
            self.vn100,
            BINARY_ASYNC_MODE_SERIAL_2,
            8,
            BG1_QTN|BG1_ACCEL|BG1_ANGULAR_RATE|BG1_MAG_PRES,
            BG3_NONE,
            BG5_NONE,
            True)
        if err_code != VNERR_NO_ERROR:
            raise Exception('Error code: %d' % err_code)
        err_code = vn100_registerAsyncDataReceivedListener(self.vn100, self.__data_listener)
        if err_code != VNERR_NO_ERROR:
            raise Exception('Error code: %d' % err_code)

    def stop(self):
        err_code = vn100_unregisterAsyncDataReceivedListener(self.vn100, self.__data_listener);
        if err_code != VNERR_NO_ERROR:
            raise Exception('Error code: %d' % err_code)
        err_code = vn100_disconnect(self.vn100);
        if err_code != VNERR_NO_ERROR:
            raise Exception('Error code: %d' % err_code)

    def get_quaternion(self):
        return self.__latest_quaternion

    def get_all_sensor_data(self):
        return self.__latest_acceleration + self.__latest_angular_rate + self.__latest_magnetic

    def __data_listener(self, sender, data):
        self.__latest_quaternion = (data.quaternion.x, data.quaternion.y, data.quaternion.z, data.quaternion.w)
        self.__latest_acceleration = (data.acceleration.c0, data.acceleration.c1, data.acceleration.c2)
        self.__latest_angular_rate = (data.angularRate.c0, data.angularRate.c1, data.angularRate.c2)
        self.__latest_magnetic = (data.magnetic.c0, data.magnetic.c1, data.magnetic.c2)
