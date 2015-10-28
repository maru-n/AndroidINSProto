#!/usr/bin/env python

import serial
from time import sleep, clock
from optparse import OptionParser


def main():
    parser = OptionParser(usage="usage: %prog [options] device_name command *command_args")
    parser.add_option("-b", "--baudrate", dest="baudrate", type='int',
                      default=None, help="serial baud rate")
    (opts, args) = parser.parse_args()

    if len(args) < 2:
        parser.print_help()
        return

    deviceName = args[0]

    if opts.baudrate:
        baudrate = opts.baudrate
    else:
        baudrate = detect_baud_rate(deviceName)
        if baudrate is None:
            print("Failed to detect current baudrate. Please reset device.")
            return
        print("Detected baudrate: ", baudrate)
        return

    command = args[1]

    commandArgs = args[2:]

    send_command(deviceName, baudrate, command, *commandArgs, printResult=True)


baudrate_list = [
    9600,
    19200,
    38400,
    57600,
    115200,
    128000,
    230400,
    460800,
    921600
    ]

COMMAND_RESPONSE_WAIT_TIME = 0.1

def detect_baud_rate(deviceName):
    serialDevice = serial.Serial(deviceName, timeout=0, writeTimeout=0)
    for br in baudrate_list:
        serialDevice.baudrate = br
        send_serial_message(serialDevice, "$VNRRG,1*XX\n")
        start = clock()
        while (clock()-start) < COMMAND_RESPONSE_WAIT_TIME:
            raw_l = serialDevice.readline()
            try:
                s = raw_l.decode()[:3]
                if s == '$VN':
                    serialDevice.close()
                    return br
            except Exception as e:
                pass
    serialDevice.close()
    return None

def send_command(deviceName, baudrate, command, *commandArgs, printResult=False):
    serialCommand = "$VN" + command + ','.join([""] + list(commandArgs)) + "*XX\n"
    serialDevice = serial.Serial(deviceName, baudrate, timeout=0)

    if printResult:
        print("Command :", serialCommand, end="")
    send_serial_message(serialDevice, serialCommand)

    correct_response = '$VN' + command
    error_response = '$VNERR'
    response = None
    successed = False
    start = clock()
    while (clock()-start) < COMMAND_RESPONSE_WAIT_TIME:
        try:
            l = serialDevice.readline().decode()
            if l.count(correct_response):
                response = l
                successed = True
                break
            elif l.count(error_response):
                response = l
                successed = False
        except Exception as e:
            pass

    serialDevice.close()

    if printResult:
        print("Response:", response)

    return successed


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
