#!/usr/bin/env python

import sys
from data_receiver import DataReceiver
from optparse import OptionParser
import glob
from sys import platform
import serial
import web_ui


def select_serial_device(args):
    if len(args) < 1:
        serial_device = choice_serial_device()
    else:
        serial_device = args[0]
    return serial_device


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


def cui_start(data_receiver):
    while True:
        try:
            ax, ay, az, gx, gy, gz, mx, my, mz = data_receiver.fetch_all_data()
            msg = ''
            msg += 'accel(x:% 9.5f y:% 9.5f z:% 9.5f)  ' % (ax, ay, az)
            msg += 'gyro(x:% 9.5f y:% 9.5f z:% 9.5f)  ' % (gx, gy, gz)
            msg += 'mag(x:% 10.5f y:% 10.5f z:% 10.5f)' % (mx, my, mz)
        except Exception:
            msg = "no data available."
        finally:
            sys.stdout.write('\r\033[K' + msg)
            sys.stdout.flush()


if __name__ == '__main__':
    parser = OptionParser()

    parser.add_option("-f", "--file", dest="filename",
                      help="write report to FILE", metavar="FILE")

    parser.add_option("-w", "--web-ui",
                      action="store_true", dest="web_ui", default=False,
                      help="use web UI.")

    (opts, args) = parser.parse_args()

    data_receiver = DataReceiver()
    serial_device = select_serial_device(args)
    data_receiver.set_serial_settings(serial_device)

    if opts.web_ui:
        web_ui.start(data_receiver)
    else:
        cui_start(data_receiver)
