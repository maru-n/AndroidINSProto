#!/usr/bin/env python

import serial
import sys

def main():
    if len(sys.argv) < 3:
        print("Usage:")
        print("\t" + sys.argv[0].split('/')[-1] + " [device_name] [command] [*command_args]")
        return
    deviceName = sys.argv[1]
    command = sys.argv[2]
    args = sys.argv[3:]
    send_command(deviceName, command, *args)


def send_command(deviceName, command, *commandArgs):

    serialCommand = "$VN" + command + ','.join([""] + list(commandArgs)) + "*XX\n"
    serialDevice = serial.Serial(deviceName, 115200, timeout=1.0)

    # stop async output
    switch_async_output(serialDevice, False)

    print("Command : " + serialCommand, end="")
    send_serial_message(serialDevice, serialCommand)
    lines = serialDevice.readlines()
    response = lines[-1].decode()
    print("Response: " + response)

    # resume async output
    switch_async_output(serialDevice, True)

    serialDevice.close()


def switch_async_output(serialDevice, on=True):
    if on:
        command = "$VNASY,1*XX\n"
    else:
        command = "$VNASY,0*XX\n"
    send_serial_message(serialDevice, command)


def send_serial_message(serialDevice, command):
    byteCommand = command.encode()
    ret = serialDevice.write(byteCommand)
    if ret != len(byteCommand):
        Exception("error occured on write serial code.")


if __name__ == '__main__':
    main()
