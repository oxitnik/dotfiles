#!/usr/bin/env bash

mkdir -p /etc/apt/apt.conf.d

CONF_FILE=/etc/apt/apt.conf.d/99user-conf

echo 'APT::Install-Recommends "false";' > $CONF_FILE
echo 'APT::Install-Suggests "false";' >> $CONF_FILE
echo 'Acquire::Pdiffs "no";' >> $CONF_FILE

