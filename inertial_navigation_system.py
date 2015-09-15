#!/usr/bin/env python

from abc import ABCMeta, abstractmethod
import serial
import struct
import time
import numpy as np


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
    def get_time(self):
        pass

    @abstractmethod
    def get_quaternion(self):
        pass

    @abstractmethod
    def get_all_sensor_data(self):
        pass

    @abstractmethod
    def get_velocity(self):
        pass

    @abstractmethod
    def get_position(self):
        pass


class AndroidINS(INS):
    def __init__(self, serial_device_name, serial_baudrate=115200, serial_timeout=0.1):
        super(AndroidINS, self).__init__()
        self.__serial_device_name = serial_device_name
        self._serial_baudrate = serial_baudrate
        self._serial_timeout = serial_timeout

    def start(self):
        self.__serial = serial.Serial(self.__serial_device_name,
                                      self._serial_baudrate,
                                      timeout=self._serial_timeout)

    def stop(self):
        try:
            self.__serial.close()
        except:
            pass

    def get_time(self):
        return time.time()

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

    def get_velocity(self):
        # Dummpy data!!
        return (0., 0., 0.)

    def get_position(self):
        # Dummpy data!!
        return (0., 0., 0.)


from vectornav import *

class VN100INS(INS):
    def __init__(self, serial_device_name):
        super(VN100INS, self).__init__()
        self.__serial_device_name = serial_device_name
        self.reset_data()
        self.__logging = False

    def start(self, logging=False):
        self.__setup_vn100()
        if logging:
            self.start_logging()


    def __setup_vn100(self):
        self.vn100 = Vn100()
        err_code = vn100_connect(self.vn100, self.__serial_device_name, 115200)
        if err_code != VNERR_NO_ERROR:
            raise Exception('Failed to connect to vn100. (Error code:%d)' % err_code)
        err_code = vn100_setAsynchronousDataOutputType(self.vn100, VNASYNC_OFF, True)
        if err_code != VNERR_NO_ERROR:
            raise Exception('Failed to disabe asynchronous ascii output. (Error code:%d)' % err_code)
        err_code = vn100_setBinaryOutput1Configuration(
            self.vn100,
            BINARY_ASYNC_MODE_SERIAL_2,
            8,
            BG1_TIME_STARTUP|BG1_DELTA_THETA|BG1_QTN,
            BG3_ACCEL|BG3_GYRO|BG3_MAG,
            BG5_NONE,
            True)
        if err_code != VNERR_NO_ERROR:
            raise Exception('Failed to set binary output configuration. (Error code:%d)' % err_code)
        err_code = vn100_registerAsyncDataReceivedListener(self.vn100, self.__data_listener)
        if err_code != VNERR_NO_ERROR:
            raise Exception('Failed to register asynchronous data receiver. (Error code:%d)' % err_code)

    def stop(self):
        err_code = vn100_unregisterAsyncDataReceivedListener(self.vn100, self.__data_listener);
        # if err_code != VNERR_NO_ERROR:
        #     raise Exception('Error code: %d' % err_code)
        err_code = vn100_disconnect(self.vn100);
        # if err_code != VNERR_NO_ERROR:
        #     raise Exception('Error code: %d' % err_code)

    def reset_data(self):
        self.__time = 0.
        self.__time_offset = None
        self.__qternion = [0., 0., 0., 0.]
        self.__acceleration = [0., 0., 0.]
        self.__angular_rate = [0., 0., 0.]
        self.__magnetic = [0., 0., 0.]
        self.__vel = [0., 0., 0.]
        self.__pos = [0., 0., 0.]

    def get_time(self):
        return self.__time

    def get_quaternion(self):
        return self.__quaternion

    def get_all_sensor_data(self):
        return self.__acceleration + self.__angular_rate + self.__magnetic

    def get_velocity(self):
        return self.__vel

    def get_position(self):
        return self.__pos

    def __init_log(self):
        self.__time_log = []
        self.__qternion_log = []
        self.__acceleration_log = []
        self.__angular_rate_log = []
        self.__magnetic_log = []
        self.__vel_log = []
        self.__pos_log = []

    def start_logging(self):
        if not self.__logging:
            self.__init_log()
        self.__logging = True

    def stop_logging(self):
        self.__logging = False

    def is_logging(self):
        return self.__logging

    def save_logfile(self, filename):
        if self.__logging:
            Exception('Couldn\'t save log during logging. Stop logging before save it.')
        np.savez(filename,
                 time = np.array(self.__time_log),
                 qtn = np.array(self.__qternion_log),
                 acl = np.array(self.__acceleration_log),
                 ang = np.array(self.__angular_rate_log),
                 mag = np.array(self.__magnetic_log),
                 vel = np.array(self.__vel_log),
                 pos = np.array(self.__pos_log)
                 )


    def __data_listener(self, sender, data):
        if self.__time_offset is None:
            self.__time_offset = data.timeStartup * 1e-9
        self.__time = data.timeStartup * 1e-9 - self.__time_offset
        self.__quaternion = (data.quaternion.x, data.quaternion.y, data.quaternion.z, data.quaternion.w)
        self.__acceleration = (data.acceleration.c0, data.acceleration.c1, data.acceleration.c2)
        self.__angular_rate = (data.angularRate.c0, data.angularRate.c1, data.angularRate.c2)
        self.__magnetic = (data.magnetic.c0, data.magnetic.c1, data.magnetic.c2)

        dt = data.deltaTime
        pre_vel = list(self.__vel)
        self.__vel[0] += data.deltaVelocity.c0
        self.__vel[1] += data.deltaVelocity.c1
        self.__vel[2] += data.deltaVelocity.c2

        self.__pos[0] += (self.__vel[0] + pre_vel[0]) * dt * 0.5
        self.__pos[1] += (self.__vel[1] + pre_vel[1]) * dt * 0.5
        self.__pos[2] += (self.__vel[2] + pre_vel[2]) * dt * 0.5

        if self.__logging:
            self.__time_log.append(self.__time)
            self.__qternion_log.append(list(self.__quaternion))
            self.__acceleration_log.append(list(self.__acceleration))
            self.__angular_rate_log.append(list(self.__angular_rate))
            self.__magnetic_log.append(list(self.__magnetic))
            self.__vel_log.append(list(self.__vel))
            #self.__pos_log.appned(list(self.__pos))
