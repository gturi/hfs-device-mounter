#!/bin/bash

check_installation () {
    command -v $1 >/dev/null 2>&1 || {
        echo -e "\n$1 missing, starting install procedure"
        sudo apt-get install $1
    }
}

dependencies=( "lsblk" "udisksctl" "hfsplus" "hfsutils" "hfsprogs" )
for i in "${dependencies[@]}"
do
    check_installation $i
done
