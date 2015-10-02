#!/usr/bin/env python

import serial
from optparse import OptionParser


def main():
    parser = OptionParser(usage="usage: %prog [options] device_name command *command_args")
    parser.add_option("-b", "--baudrate", dest="baudrate", type='int',
                      default=115200, help="serial baud rate")
    (opts, args) = parser.parse_args()

    if len(args) < 2:
        parser.print_help()
        return

    send_command(args[0], opts.baudrate, args[1], *args[2:], printResult=True)


def send_command(deviceName, baudrate, command, *commandArgs, printResult=False):
    serialCommand = "$VN" + command + ','.join([""] + list(commandArgs)) + "*XX\n"
    serialDevice = serial.Serial(deviceName, baudrate, timeout=1.0)

    # stop async output
    switch_async_output(serialDevice, False)
    if printResult:
        print("Command : " + serialCommand, end="")
    send_serial_message(serialDevice, serialCommand)
    lines = serialDevice.readlines(1000)  # line number limitation is to avoid timeout problem on readlines()
    # resume async output
    switch_async_output(serialDevice, True)

    serialDevice.close()

    if len(lines) == 0:
        if printResult:
            print("Response: none")
        return False

    try:
        response = lines[-1].decode()
    except UnicodeDecodeError:
        if printResult:
            print("Response: invalid")
        return False

    if printResult:
        print("Response: " + response, end="")

    if response.find('$VN'+command) == -1:
        return False
    else:
        return True


def write_register(deviceName, baudrate, registerId, *args, printResult=False):
    return send_command(deviceName, baudrate, "WRG", *([str(registerId)] + [str(a) for a in args]), printResult=printResult)


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
