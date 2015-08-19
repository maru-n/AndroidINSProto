#!/usr/bin/env python

import sys


def start(ins):
    clr_txt = ''
    while True:
        msg = clr_txt
        try:
            ax, ay, az, gx, gy, gz, mx, my, mz = ins.get_all_sensor_data()
            msg += 'accel(x:% 9.5f y:% 9.5f z:% 9.5f)  ' % (ax, ay, az)
            msg += 'gyro(x:% 9.5f y:% 9.5f z:% 9.5f)  ' % (gx, gy, gz)
            msg += 'mag(x:% 10.5f y:% 10.5f z:% 10.5f)' % (mx, my, mz)
            x, y, z, w = ins.get_quaternion()
            msg += '\n'
            msg += 'q(x:% 9.5f y:% 9.5f z:% 9.5f w:% 9.5f)  ' % (x, y, z, w)
            clr_txt = '\r\033[K\033[1A\033[K'

        except Exception:
            msg += 'no data available.'
            clr_txt = '\r\033[K'
        finally:
            sys.stdout.write(msg)
            sys.stdout.flush()
