#!/usr/bin/python
'''
Author: Pryz
Description: Class Report
	     Used in inventory.py to generate the VM list report 
'''
import subprocess
import re
import simplejson as json
from pysphere import VIServer

class Report:
    """Class report. Generate a dictionnary with the VMs and these properties"""

    def __init__(self, config):
        self.login = config['user']
        self.password = config['password']
        self.vcenter = config['vcenter']
        self.server = VIServer()

    def connect(self):
        """Connect to the hypervisor"""
        self.server.connect(self.vcenter, self.login, self.password)

    def disconnect(self):
        """Close the connection with the hypervisor"""
        if self.server:
            self.server.disconnect()

    def generate_report(self):
        """Generate the report of the actual connection"""
        report = []
        # Create the report
        vms_list = self.server.get_registered_vms()
        for vm_path in vms_list:
            virtual_machine = self.server.get_vm_by_path(vm_path)
            if str(virtual_machine.__class__) != "pysphere.vi_virtual_machine.VIVirtualMachine":
                continue
            if re.match(r'rhel', virtual_machine.get_property('guest_id')):
                vm_infos = { 
                    'name': virtual_machine.get_property('name'), 
                    'ip': virtual_machine.get_property('ip_address'),
                    'os': virtual_machine.get_property('guest_id')
                }
            try:
                status = virtual_machine.get_status()
            except Exception, e:
                print "Couldn't do it: %s" % e
                vm_infos['powered'] = 'none'
                report.append(vm_infos)
                continue
            if status == "POWERED ON":
                vm_infos['powered'] = 'on'
                # Get version in ssh 
                ssh = subprocess.Popen([
                  "ssh", 
                  "-i ~/.ssh/id_rsa", 
                  "%s" % vm_infos['name'],
                  "cat /etc/redhat-release"],
                  shell=False,  stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                release = ssh.stdout.readlines()
                if release == []:
                    error = ssh.stderr.readlines()
                    vm_infos['release'] = "error: " + error
                else:
                    regex = re.compile("release (\d.*).+\(\D*(\d*)\)")
                    r = regex.search(release[0])
                    release = r.groups()
                    if release[1].strip():
                        vm_infos['release'] = release[0] + "." + release[1]
                    else:
                        vm_infos['release'] = release[0]
            else:
                vm_infos['powered'] = 'off'
        report.append(vm_infos)

        return report

    def report_to_file(self, report):
        """Write the report a vm_list_infos.json file"""
        f = open('data/vm_list_infos.json', 'wb')
        f.write(json.dumps(report))
        f.close()

