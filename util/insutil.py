#!/usr/bin/env python

import vnutil
import sys

serial_device_name = None
available_baudrate = [115200, 921600]
baudrate = 921600


def setup():
    print("Baudrate... ", end="", flush=True)
    for br in available_baudrate:
        if vnutil.write_register(serial_device_name, br, 5, baudrate):
            print("\033[32mOK\033[39m\n")
            break
    else:
        print("\033[31mError\033[39m\n")
        return


def reset():
    print("Reset... ", end="", flush=True)
    for br in available_baudrate:
        if vnutil.send_command(serial_device_name, br, 'RFS'):
            print("\033[32mOK\033[39m\n")
            break
    else:
        print("\033[31mError\033[39m\n")
        return


from optparse import OptionParser

if __name__ == '__main__':
    parser = OptionParser()
    (opts, args) = parser.parse_args()
    if len(args) != 2:
        parser.print_help()

    serial_device_name = args[0]

    if args[1] == "setup":
        setup()
    elif args[1] == "reset":
        reset()
    else:
        parser.print_help()
