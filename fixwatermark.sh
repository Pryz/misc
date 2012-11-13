#!/bin/sh
# Delete the watermark of the ATI Drivers

DRIVER=/lib64/xorg/modules/drivers/fglrx_drv.so

for x in $(objdump -d $DRIVER|awk '/call/&&/EnableLogo/{print "\\x"$2"\\x"$3"\\x"$4"\\x"$5"\\x"$6}'); do
  sed -i "s/$x/\x90\x90\x90\x90\x90/g" $DRIVER
done
