#!/usr/bin/python3

import sys
import re
import subprocess
import json
import getpass
import argparse


# parsing program flags
parser = argparse.ArgumentParser()
parser.add_argument('-d', action='store_true',
                    help='check and install program dependencies')
parser.add_argument('-c', action='store_true',
                    help='check the device filesystem with fsck')
parser.add_argument('-m', action='store_false',
                    help='use [umount|mount] instead of udisksctl [unmount|mount] (requires root privileges)')

flags = parser.parse_args()

# check program dependencies
if flags.d:
    print('checking that all the dependencies are satisfied')
    subprocess.call(['./dependencies.sh'])
    print('\n\n')

# --- #


def runCommand(cmd: str):
    print(cmd)
    subprocess.call(cmd.split())


def runCommandList(cmd: list):
    print(' '.join(cmd))
    subprocess.call(cmd)

def mode(cmd1, cmd2):
    if flags.m: 
        return cmd1
    else:
        return cmd2

fstype = 'hfs'

stdout = subprocess.check_output(['lsblk', '-flJ'])

json_lsblk: dict = json.loads(str(stdout, 'utf-8'))

# filtering out non hfs filesystems
hfs_devices: list = [x for x in json_lsblk['blockdevices']
                     if fstype in str(x['fstype'])]

if len(hfs_devices) <= 0:
    sys.exit('No hfs device found, quitting...')

# device selection
valid_input: bool = False
while not valid_input:
    print('Currently detected hfs devices:')
    for idx, device in enumerate(hfs_devices):
        print(str(idx) + ') [name]=' + str(device['name']) + ' [label]=' +
              str(device['label']) + ' [mountpoint]=' + str(device['mountpoint']))

    try:
        selected: int = int(input('\nType the number of the hfs device to mount' +
                                  ' with read/write permissions: '))
    except ValueError:
        print('Wrong input\n')
        continue
    else:
        if selected < len(hfs_devices):
            valid_input = True


user: str = getpass.getuser()
device = hfs_devices[selected]
name: str = '/dev/' + device['name']

print(device['mountpoint'])
if device['mountpoint'] is None:
    mountpoint = '/media/' + user + '/' + str(device['label'])
else:
    mountpoint = str(device['mountpoint'])
    # unmount device
    cmd1 = 'udisksctl unmount -b ' + name
    cmd2 = 'sudo umount ' + name
    runCommand(mode(cmd1, cmd2))

# trasform mountpoint in list to avoid errors caused by spaces
mountpoint = [mountpoint]

if flags.c:
    # checks the device filesystem;
    # useful if the device was unproperly unmounted or
    # has become partially corrupted
    runCommand('sudo fsck.hfsplus -f ' + name)

# mounts the hfs device with read and write permissions
if flags.m:
    cmd = 'udisksctl mount -t hfsplus -o force,rw -b ' + name
    runCommand(cmd)
else:
    cmd = 'sudo mkdir -m 777'
    runCommandList(cmd.split() + mountpoint)

    cmd = 'sudo mount -t hfsplus -o force,rw ' + name
    runCommandList(cmd.split() + mountpoint)
