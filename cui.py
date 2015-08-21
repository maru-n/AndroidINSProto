#!/usr/bin/env python

import sys
import time

def start(ins):
    clr_txt = ''
    while True:
        pass

        msg = clr_txt
        try:
            ax, ay, az, gx, gy, gz, mx, my, mz = ins.get_all_sensor_data()
            msg += 'accel(x:% 10.5f y:% 10.5f z:% 10.5f)\n' % (ax, ay, az)
            msg += 'ang_r(x:% 10.5f y:% 10.5f z:% 10.5f)\n' % (gx, gy, gz)
            msg += 'magnt(x:% 10.5f y:% 10.5f z:% 10.5f)\n' % (mx, my, mz)
            x, y, z, w = ins.get_quaternion()
            msg += 'qtn(x:% 9.5f y:% 9.5f z:% 9.5f w:% 9.5f)  ' % (x, y, z, w)
            clr_txt = '\r\033[K\033[1A\033[K\033[1A\033[K\033[1A\033[K'

        except Exception:
            msg += 'no data available.'
            clr_txt = '\r\033[K'
        finally:
            sys.stdout.write(msg)
            sys.stdout.flush()

        time.sleep(0.1)
