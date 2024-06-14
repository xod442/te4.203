#!/usr/bin/env python3

from requests.packages.urllib3.exceptions import InsecureRequestWarning
import pyafc.vcenter as afc_vcenter
import urllib3
import logging

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.basicConfig(level=logging.INFO)


def get_host_by_hostname_and_vsphere(hostname, vsphere_name, auth_header, **kwargs):
	pack_config_uuid = afc_vcenter.get_uuid_by_vsphere_hostname(vsphere_name, auth_header, **kwargs)
	print(f"vsphere_pack_id: {pack_config_uuid}")
	host_dict = get_all(auth_header, **kwargs)
	for host in host_dict:
		if host["name"].casefold() == hostname.casefold() and \
				host['associated_objects']['vmware']['pack_config_uuid'] == pack_config_uuid:
			return host
	return {}


def get_host_uuid_by_hostname_and_vsphere(hostname, vsphere_name, auth_header, **kwargs):
	host = get_host_by_hostname_and_vsphere(hostname, vsphere_name, auth_header, **kwargs)
	return host['associated_objects']['vmware']['uuid']


def list_hostnic_uuid_by_nicname_hostname_and_vsphere(nicnamelist, hostname, vsphere_name, auth_header, host_nic_infix="pnic", **kwargs):
	hostnic_uuid_list = []
	for nicname in nicnamelist:
		host_uuid = get_host_uuid_by_hostname_and_vsphere(hostname, vsphere_name, auth_header, **kwargs)
		hostnic_uuid_list.append(f"{host_uuid}-{host_nic_infix}-{nicname}")
	return hostnic_uuid_list


def get_vm_uuid_by_vmname_hostname_and_vsphere(vmname, hostname, vsphere_name, auth_header, **kwargs):
	host = get_host_by_hostname_and_vsphere(hostname, vsphere_name, auth_header, **kwargs)
	vm_dict = host['vms']
	for vm in vm_dict:
		if vm["name"].casefold() == vmname.casefold():
			return vm['associated_objects']['vmware']['uuid']
	return ''


def list_vmnic_uuid_by_vmnamelist_hostname_and_vsphere(vmnamelist, hostname, vsphere_name, auth_header, vm_nic_suffix="vnic-Network-adapter-2",**kwargs):
	vmnic_uuid_list = []
	for vmname in vmnamelist:
		vm_uuid = get_vm_uuid_by_vmname_hostname_and_vsphere(
			vmname['name'],
			hostname,
			vsphere_name,
			auth_header,
			**kwargs
		)
		vmnic_uuid_list.append(vm_uuid+"-"+vm_nic_suffix)
	return vmnic_uuid_list


def get_all(auth_header, **kwargs):
	target_url = kwargs["url"] + "hosts"
	# print("Target_url: " + target_url)
	response = kwargs["s"].get(target_url, headers=auth_header, verify=False)
	if response.status_code not in [200]:
		logging.warning("FAIL: get_all hosts failed with status code %d: %s" % (response.status_code, response.text))
		exit(-1)
	else:
		logging.info("SUCCESS: get_all hosts succeeded")
		output = response.json()
		return output['result']