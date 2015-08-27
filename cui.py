#!/usr/bin/env python

import sys
import time

def start(ins):
    sys.stdout.write('Start!!\n')
    clr_txt = ''
    while True:
        pass

        msg = ''
        try:
            ax, ay, az, gx, gy, gz, mx, my, mz = ins.get_all_sensor_data()
            qx, qy, qz, qw = ins.get_quaternion()
            vx, vy, vz = ins.get_velocity()
            rx, ry, rz = ins.get_position()
            msg += 'accel(x:% 10.5f y:% 10.5f z:% 10.5f)\n' % (ax, ay, az)
            msg += 'angrt(x:% 10.5f y:% 10.5f z:% 10.5f)\n' % (gx, gy, gz)
            msg += 'magnt(x:% 10.5f y:% 10.5f z:% 10.5f)\n' % (mx, my, mz)
            msg += 'qtn(x:% 9.5f y:% 9.5f z:% 9.5f w:% 9.5f)  \n' % (qx, qy, qz, qw)
            msg += 'vel(x:% 9.5f y:% 9.5f z:% 9.5f)  \n' % (vx, vy, vz)
            msg += 'pos(x:% 9.5f y:% 9.5f z:% 9.5f)  \n' % (rx, ry, rz)

        except Exception:
            msg += 'no data available.\n'

        finally:
            sys.stdout.write(clr_txt + msg)
            sys.stdout.flush()
            clr_txt = '\033[1A\033[K' * msg.count('\n')

        time.sleep(0.1)
