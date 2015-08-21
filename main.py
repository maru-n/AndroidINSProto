#!/usr/bin/env python

from inertial_navigation_system import *
import web_ui
import cui
from sys import platform
import serial
import glob
from optparse import OptionParser


def choice_serial_device():
    devices = get_available_serial_devices()
    while True:
        for i in range(len(devices)):
            print('%2d: %s' % (i, devices[i]))
        key_input = input('please select device: ')
        try:
            di = int(key_input)
            if di < len(devices):
                break
        except:
            pass
    return devices[di]


def get_available_serial_devices():
    if platform.startswith('win'):
        ports = ['COM' + str(i + 1) for i in range(256)]
    elif platform.startswith('linux') or platform.startswith('cygwin'):
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


if __name__ == '__main__':
    parser = OptionParser()

    parser.add_option("-w", "--web-ui",
                      action="store_true", dest="web_ui", default=False,
                      help="use web UI.")

    (opts, args) = parser.parse_args()

    if len(args) < 1:
        serial_device = choice_serial_device()
    else:
        serial_device = args[0]

    #ins = AndroidINS(serial_device)
    ins = VN100INS(serial_device)
    ins.start()

    if opts.web_ui:
        web_ui.start(ins)
    else:
        cui.start(ins)
