#!/usr/bin/python
'''
Author: Pryz
Description: Get current status and properties of a VM with pysphere 
'''
from pysphere import VIServer

# Connect to the vcenter
LOGIN = "user"
PWD = "password"
VCENTER = "vcenter.labo.fr"
SERVER = VIServer()
SERVER.connect(VCENTER, LOGIN, PWD)

VMNAME = "vm1.labo.fr"
VM = SERVER.get_vm_by_name(VMNAME)
print VM.get_status()
print VM.get_property('ip_address')
print VM.get_properties()

# Close connection
SERVER.disconnect()

