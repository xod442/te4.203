from pyVmomi import vim
from pyVim.task import WaitForTask

import logging

def list_dvs_switches(content):
    dvs_view = content.viewManager.CreateContainerView(content.rootFolder, [vim.DistributedVirtualSwitch], True)
    dvs_list = dvs_view.view
    dvs_view.Destroy()
    return dvs_list

def list_networks(content):
    network_view = content.viewManager.CreateContainerView(content.rootFolder, [vim.Network], True)
    networks = network_view.view
    network_view.Destroy()
    return networks


# Function to find a virtual machine by its name
def find_vm_by_name(content, vm_name):
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
    for vm in container.view:
        if vm.name == vm_name:
            return vm
    return None

# Function to find a distributed virtual switch by its name
def find_dvs_by_name(content, dvs_name):
    dvs_view = content.viewManager.CreateContainerView(content.rootFolder, [vim.DistributedVirtualSwitch], True)
    for switch in dvs_view.view:
        if switch.name == dvs_name:
            return switch
    return None


def find_dvs_portgroup_by_name(content, dvs_name, portgroup_name):
    dvs = find_dvs_by_name(content, dvs_name)
    if dvs:
        portgroup = find_portgroup_by_name(content, dvs, portgroup_name)
        return portgroup
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

def connect_vnic_to_portgroup(vm, portgroup_key, vnic_mac, switch_uuid, portgroup_name, portKey):
    print('blue')
    devices = vm.config.hardware.device
    for device in devices:
        if isinstance(device, vim.vm.device.VirtualVmxnet3) and device.macAddress == vnic_mac:
            # bprint(device.backing.port.switchUuid)

            nic_spec = vim.vm.device.VirtualDeviceSpec()
            nic_spec.device = device
            nic_spec.device.connectable.connected = True
            nic_spec.device.deviceInfo.summary = portgroup_name
            nic_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.edit
            nic_spec.device.backing.port.switchUuid = switch_uuid
            nic_spec.device.backing.port.portgroupKey = portgroup_key
            nic_spec.device.backing.port.portKey = portKey
            #
            config_spec = vim.vm.ConfigSpec(deviceChange=[nic_spec])
            # print(nic_spec)
            vm.ReconfigVM_Task(config_spec)
            print("Successfully connected vNIC with MAC {} to DVS port group.".format(vnic_mac))

            return
    print("No vNIC found with MAC {} on the VM.".format(vnic_mac))

    return None
