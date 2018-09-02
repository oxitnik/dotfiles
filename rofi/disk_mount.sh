#!/usr/bin/env bash

is_mounted() {
    findmnt -no TARGET "${1}" >/dev/null 2>&1
}


if [ -n "$1" ]
then    
    device_name=$(echo $1 | cut -d':' -f1);
    device_action=$(echo $1 | cut -d':' -f2);

    if is_mounted ${device_name}; then
        udisksctl unmount --block-device ${device_name} > /dev/null 2>&1
    else
        if [[ "$device_action" == '(eject)' ]]; then
            udisksctl poweroff \
                --block-device ${device_name} > /dev/null 2>&1
        else
            udisksctl mount \
                --options nosuid,noexec,noatime \
                --block-device ${device_name} > /dev/null 2>&1
        fi
    fi
fi

all_devices=( $(lsblk -plno NAME) )

for dev_name in ${all_devices[@]}; do
    dev_type=$(lsblk -drno TYPE "$dev_name");
    if [[ "$(lsblk -drno RM "${dev_name}")" == '1' ]]; then
        is_removable=1;
    else
        is_removable=0;
    fi
    if [[ "${all_devices[@]}" =~ ${dev_name}1 ]]; then
        has_partitions=1;
    else
        has_partitions=0;
    fi

    device_model=$(echo -e $(lsblk -drno MODEL ${dev_name}))

    should_show=0

    if [[ $is_removable == 1 ]]; then
        if [[ "$dev_type" == 'disk' && $has_partitions != -1 ]]; then
            should_show=1;
        fi
        if [[ "$dev_type" == 'part' ]]; then
            should_show=1;
        fi
    fi

    if [[ $should_show == 1 ]]; then
        line_str="$dev_name:$device_model";
        eject_str=""
        if is_mounted "${dev_name}"; then
            mount_point=$(lsblk -drno MOUNTPOINT ${dev_name})
            line_str="$line_str (mounted $mount_point)"
        else
            eject_str="$line_str:(eject)"
        fi
        echo $line_str;
        if [[ $eject_str != "" ]]; then
            echo $eject_str;
        fi
    fi
done

