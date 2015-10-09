#!/usr/bin/env python

import sys
import time
import os

import sys
import select
import tty
import termios
from datetime import datetime


class NonBlockingConsole(object):

    def __enter__(self):
        self.old_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())
        return self

    def __exit__(self, type, value, traceback):
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)


    def get_data(self):
        if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
            return sys.stdin.read(1)
        return False


def start(ins):
    sys.stdout.write('\nr: reset data   l: start/stop log   q,ESC: quit\n')
    with NonBlockingConsole() as nbc:
        clr_txt = ''
        while True:

            key = nbc.get_data()
            if key in ['\x1b', 'q']:
                break
            elif key in ['l']:
                if ins.is_logging():
                    ins.stop_logging()
                    filename = os.path.join(os.getcwd(), datetime.now().strftime('%Y%m%d_%H%M%S'))
                    ins.save_logfile(filename)
                else:
                    ins.start_logging()
            elif key in ['r']:
                ins.reset_data()

            msg = ''
            try:
                t = ins.get_time()
                ax, ay, az, gx, gy, gz, mx, my, mz = ins.get_all_sensor_data()
                qx, qy, qz, qw = ins.get_quaternion()
                dvx, dvy, dvz, vx, vy, vz, rx, ry, rz = ins.get_navigation_state()
                msg += 'time:% 10.2f\n' % t
                msg += 'accel(x:% 10.5f y:% 10.5f z:% 10.5f)\n' % (ax, ay, az)
                msg += 'angrt(x:% 10.5f y:% 10.5f z:% 10.5f)\n' % (gx, gy, gz)
                msg += 'magnt(x:% 10.5f y:% 10.5f z:% 10.5f)\n' % (mx, my, mz)
                msg += 'qtn(x:% 9.5f y:% 9.5f z:% 9.5f w:% 9.5f)  \n' % (qx, qy, qz, qw)
                msg += 'd_v(x:% 9.5f y:% 9.5f z:% 9.5f)  \n' % (dvx, dvy, dvz)
                msg += 'vel(x:% 9.5f y:% 9.5f z:% 9.5f)  \n' % (vx, vy, vz)
                msg += 'pos(x:% 9.5f y:% 9.5f z:% 9.5f)  \n' % (rx, ry, rz)
                if ins.is_logging():
                    msg += "\033[31m[Recording]\033[39m\n"

            except Exception:
                msg += 'no data available.\n'

            finally:
                sys.stdout.write(clr_txt + msg)
                sys.stdout.flush()
                clr_txt = '\033[1A\033[K' * msg.count('\n')

            time.sleep(0.1)
