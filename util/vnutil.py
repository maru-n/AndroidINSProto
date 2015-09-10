#!/usr/bin/env python

import serial
import sys

serialDevice = None

def main():
    global serialDevice
    deviceName = sys.argv[1]
    serialDevice = serial.Serial(deviceName, 115200, timeout=1.0)

    # stop async output
    switch_async_output(False)

    command = "$VN" + sys.argv[2] + ','.join([''] + sys.argv[3:]) + "*XX\n"
    print("Command : " + command, end="")
    send_command(command)
    lines = serialDevice.readlines()
    response = lines[-1].decode()
    print("Response: " + response)

    # resume async output
    switch_async_output(True)

    serialDevice.close()


def switch_async_output(on=True):
    if on:
        command = "$VNASY,1*XX\n"
    else:
        command = "$VNASY,0*XX\n"
    send_command(command)


def send_command(command):
    byteCommand = command.encode()
    ret = serialDevice.write(byteCommand)
    if ret != len(byteCommand):
        Exception("error occured on write serial code.")


if __name__ == '__main__':
    main()

