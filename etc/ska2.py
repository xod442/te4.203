from pyVim import connect
from pyVmomi import vim
import ssl

def connect_vcenter(vcenter_ip, username, password):
    try:
        service_instance = connect.SmartConnectNoSSL(host=vcenter_ip,
                                                     user=username,
                                                     pwd=password)
        return service_instance
    except Exception as e:
        print("Unable to connect to vCenter server:", str(e))
        return None

def find_dvs_portgroup_by_name(content, dvs_name, portgroup_name):
    dvs = find_dvs_by_name(content, dvs_name)
    if dvs:
        portgroup = find_portgroup_by_name(content, dvs, portgroup_name)
        return portgroup
    else:
        return None

def find_dvs_by_name(content, dvs_name):
    dvs_view = content.viewManager.CreateContainerView(content.rootFolder, [vim.DistributedVirtualSwitch], True)
    dvs = [dvs for dvs in dvs_view.view if dvs_name == dvs.name]
    dvs_view.Destroy()
    if dvs:
        return dvs[0]
    else:
        return None

def find_portgroup_by_name(content, dvs, portgroup_name):
    portgroup_view = content.viewManager.CreateContainerView(content.rootFolder, [vim.dvs.DistributedVirtualPortgroup], True)
    portgroups = [pg for pg in portgroup_view.view if pg.config.distributedVirtualSwitch == dvs and pg.name == portgroup_name]
    portgroup_view.Destroy()
    if portgroups:
        return portgroups[0]
    else:
        return None

def find_vm_by_name(content, vm_name):
    vm_view = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
    vm = [vm for vm in vm_view.view if vm_name == vm.name]
    vm_view.Destroy()
    if vm:
        return vm[0]
    else:
        return None

def connect_vnic_to_portgroup(vm, portgroup_key):
    devices = vm.config.hardware.device
    for device in devices:
        if isinstance(device, vim.vm.device.VirtualEthernetCard):
            nic_spec = vim.vm.device.VirtualDeviceSpec()
            nic_spec.device = device
            nic_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.edit
            nic_spec.device.backing = vim.vm.device.VirtualEthernetCard.DistributedVirtualPortBackingInfo()
            nic_spec.device.backing.port = vim.dvs.PortConnection(portgroupKey=portgroup_key)
            config_spec = vim.vm.ConfigSpec(deviceChange=[nic_spec])
            vm.ReconfigVM_Task(config_spec)
            print("Successfully connected vNIC to DVS port group.")
            return
    print("No compatible network adapter found on the VM.")

def main():
    vcenter_ip = '192.168.229.245'
    username = 'arubatm@vsphere.local'
    password = 'Aruba123!@#'
    dvs_name = 'dvs01'
    portgroup_name = 'dsa-leaf-01-dvs01-11'
    vm_name = 'workload-v10-101'

    # Disabling SSL certificate verification (use only in development/testing)
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    service_instance = connect_vcenter(vcenter_ip, username, password)
    if service_instance:
        content = service_instance.RetrieveContent()

        portgroup = find_dvs_portgroup_by_name(content, dvs_name, portgroup_name)
        if portgroup:
            vm = find_vm_by_name(content, vm_name)
            if vm:
                connect_vnic_to_portgroup(vm, portgroup.key)
            else:
                print("Virtual machine with name '{}' not found.".format(vm_name))
        else:
            print("Portgroup with name '{}' not found on DVS '{}'.".format(portgroup_name, dvs_name))

        connect.Disconnect(service_instance)

if __name__ == "__main__":
    main()
