#!/usr/bin/env python

import vnutil
import sys

serial_device_name = None
baudrate = 921600


def setup():
    #reset()

    set_baudrate()
    #set_indoor_heading_mode()
    set_delta_theta_velocity_configuration()
    #set_world_magnetic_and_gravity_model()


def set_baudrate():
    print("Baudrate... ", end="", flush=True)
    current_baudrate = vnutil.detect_baud_rate(serial_device_name)
    if current_baudrate is None:
        print("\033[31mError\033[39m")
    if vnutil.write_register(serial_device_name, current_baudrate, 5, baudrate):
        print("\033[32mOK\033[39m")
    else:
        print("\033[31mError\033[39m")


def set_world_magnetic_and_gravity_model():
    print("World Magnetic and Gravity Model... ", end="", flush=True)
    if vnutil.write_register(serial_device_name, baudrate, 83, 1, 1, 0, 0, 1000, 2015, 35.689488, 139.691706, 0):
        print("\033[32mOK\033[39m")
    else:
        print("\033[31mError\033[39m")


def set_indoor_heading_mode():
    print("Indoor Heading Mode... ", end="", flush=True)
    if vnutil.write_register(serial_device_name, baudrate, 35, 1, 2, 1, 1):
        print("\033[32mOK\033[39m")
    else:
        print("\033[31mError\033[39m")

def set_delta_theta_velocity_configuration():
    print("DeltaTheta and DeltaVelocity configuration... ", end="", flush=True)
    if vnutil.write_register(serial_device_name, baudrate, 82, 1, 1, 1, 0, 0):
        print("\033[32mOK\033[39m")
    else:
        print("\033[31mError\033[39m")


def reset():
    print("Reset... ", end="", flush=True)
    for br in available_baudrate:
        if vnutil.send_command(serial_device_name, br, 'RFS'):
            print("\033[32mOK\033[39m")
            break
    else:
        print("\033[31mError\033[39m")
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
