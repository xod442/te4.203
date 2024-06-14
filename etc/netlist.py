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
portgroup_key = '16'
portgroup_name = 'dsa-leaf-01-dvs01-11'
#vnic_mac = '00:50:56:8c:0c:f8'
vnic_mac = '00:50:56:8c:a9:fa'

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

#  net list_networks
if service_instance:
    content = service_instance.RetrieveContent()

    networks = nic.list_networks(content)
    if networks:
        print("Networks in vCenter:")
        for network in networks:
            #print("- Name: {}, Type: {}".format(network.name, network.__class__.__name__))
            print(network)
    else:
        print("No networks found in vCenter.")



    dvs_list = nic.list_dvs_switches(content)
    if dvs_list:
        print("Distributed Virtual Switches in vCenter:")
        for dvs in dvs_list:
            print("- Name: {}, Switch UUID: {}".format(dvs.name, dvs.uuid))
    else:
        print("No distributed virtual switches found in vCenter.")

Disconnect(service_instance)
