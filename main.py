#!/usr/bin/env python

from data_receiver import DataReceiver
from optparse import OptionParser
import sys

if __name__ == '__main__':
    parser = OptionParser()
    (opts, args) = parser.parse_args()

    if len(args) < 1:
        exit()

    serial_device = args[0]
    data_receiver = DataReceiver()
    data_receiver.set_serial_settings(serial_device)

    while True:
        try:
            ax, ay, az, gx, gy, gz, mx, my, mz = data_receiver.fetch_all_data()
            msg = ''
            msg += 'accel(x:% 9.5f y:% 9.5f z:% 9.5f)  ' % (ax, ay, az)
            msg += 'gyro(x:% 9.5f y:% 9.5f z:% 9.5f)  ' % (gx, gy, gz)
            msg += 'mag(x:% 10.5f y:% 10.5f z:% 10.5f)' % (mx, my, mz)
        except Exception as e:
            msg = "no data available."
        finally:
            sys.stdout.write('\r\033[K' + msg)
            sys.stdout.flush()
