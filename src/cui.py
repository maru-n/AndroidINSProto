#!/usr/bin/env python

import sys
import time
import os

import sys
import select
import tty
import termios
from datetime import datetime
from threading import Timer


class NonBlockingConsole(object):

    def __enter__(self):
        self.old_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())
        return self

    def __exit__(self, type, value, traceback):
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)


    def get_data(self):
        #if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
        select.select([sys.stdin], [], [])
        return sys.stdin.read(1)
        #return False


message = ''
ins = None
running = False
saving = False

def __print_status():
    global message
    clr_txt = '\033[1A\033[K' * message.count('\n')
    message = ''
    try:
        t = ins.get_time()
        (ax, ay, az), (gx, gy, gz), (mx, my, mz) = ins.get_all_sensor_data()
        qx, qy, qz, qw = ins.get_quaternion()
        (dvx, dvy, dvz), (vx, vy, vz), (rx, ry, rz) = ins.get_navigation_state()
        message += 'time:% 10.2f\n' % t
        message += 'accel(x:% 10.5f y:% 10.5f z:% 10.5f)\n' % (ax, ay, az)
        message += 'angrt(x:% 10.5f y:% 10.5f z:% 10.5f)\n' % (gx, gy, gz)
        message += 'magnt(x:% 10.5f y:% 10.5f z:% 10.5f)\n' % (mx, my, mz)
        message += 'qtn(x:% 9.5f y:% 9.5f z:% 9.5f w:% 9.5f)  \n' % (qx, qy, qz, qw)
        message += 'd_v(x:% 9.5f y:% 9.5f z:% 9.5f)  \n' % (dvx, dvy, dvz)
        message += 'vel(x:% 9.5f y:% 9.5f z:% 9.5f)  \n' % (vx, vy, vz)
        message += 'pos(x:% 9.5f y:% 9.5f z:% 9.5f)  \n' % (rx, ry, rz)
        if ins.is_logging():
            message += "\033[31m[Recording]\033[39m\n"
        elif saving:
            message += "\033[31m[Save.....]\033[39m\n"

    except Exception:
        message += 'no data available.\n'

    finally:
        sys.stdout.write(clr_txt + message)
        sys.stdout.flush()


def __print_status_loop():
    __print_status()
    if running:
        Timer(0.2, __print_status_loop).start()


def start(_ins):
    global ins
    global running
    global saving
    running = True
    ins = _ins
    print('\nr: reset data   l: start/stop log   q,ESC: quit')
    __print_status_loop()
    with NonBlockingConsole() as nbc:
        while True:
            key = nbc.get_data()
            if key in ['\x1b', 'q']:
                running = False
                break
            elif key in ['l']:
                if ins.is_logging():
                    ins.stop_logging()
                    saving = True
                    filename = os.path.join(os.getcwd(), datetime.now().strftime('%Y%m%d_%H%M%S'))
                    ins.save_logfile(filename)
                    saving = False
                else:
                    ins.start_logging()
            elif key in ['r']:
                ins.reset_data()
