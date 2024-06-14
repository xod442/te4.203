from pyVmomi import vim
from pyVim.task import WaitForTask
from pyVim.connect import SmartConnect, Disconnect
import ssl
import logging
import utility.pod_info as pod_info
import utility.nic2dvs as nic

vsphere_ip = "192.168.229.245"
vsphere_user = "arubatm@vsphere.local"
vsphere_pass = "Aruba123!@#"
vm_name = "workload-v10-101"
dvs_name = "dvs01"
# Specific port number
portgroup_key = 'dvportgroup-6071'
portgroup_name = 'dsa-leaf-01-dvs01-10'
#vnic_mac = '00:50:56:8c:0c:f8'
vnic_mac = '00:50:56:8c:a9:fa'
switch_uuid = '50 0c 4a d7 47 42 6c 04-f3 10 39 28 83 8e f4 c3'
portKey = '10'

logging.basicConfig(filename="zero.log",
    				format='%(asctime)s %(message)s',
    				filemode='a')

sslContext = ssl._create_unverified_context()

port="443"


# Create a connector to vsphere
service_instance = SmartConnect(
                    host=vsphere_ip,
                    user=vsphere_user,
                    pwd=vsphere_pass,
                    port=port,
                    sslContext=sslContext
)


if service_instance:
    content = service_instance.RetrieveContent()

    portgroup = nic.find_dvs_portgroup_by_name(content, dvs_name, portgroup_name)
    if portgroup:
        vm = nic.find_vm_by_name(content, vm_name)
        if vm:
            nic.connect_vnic_to_portgroup(vm, portgroup_key, vnic_mac, switch_uuid, portgroup_name, portKey)
        else:
            print("Virtual machine with name '{}' not found.".format(vm_name))
    else:
        print("Portgroup with name '{}' not found on DVS '{}'.".format(portgroup_name, dvs_name))

Disconnect(service_instance)
