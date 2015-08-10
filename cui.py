#!/usr/bin/env python

import sys


def start(ins):
    while True:
        try:
            ax, ay, az, gx, gy, gz, mx, my, mz = ins.get_all_sensor_data()
            msg = ''
            msg += 'accel(x:% 9.5f y:% 9.5f z:% 9.5f)  ' % (ax, ay, az)
            msg += 'gyro(x:% 9.5f y:% 9.5f z:% 9.5f)  ' % (gx, gy, gz)
            msg += 'mag(x:% 10.5f y:% 10.5f z:% 10.5f)' % (mx, my, mz)
        except Exception:
            msg = "no data available."
        finally:
            sys.stdout.write('\r\033[K' + msg)
            sys.stdout.flush()
