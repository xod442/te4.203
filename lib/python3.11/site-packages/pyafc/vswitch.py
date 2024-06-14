#!/usr/bin/env python3

from requests.packages.urllib3.exceptions import InsecureRequestWarning
import pyafc.hosts as hosts
import urllib3
import logging

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.basicConfig(level=logging.INFO)

def create(inputdata, auth_header, **kwargs):

	# TODO: Get All vswith, this API is not avaialble at this point. Uncomment when this API
	# becomes available
	# uuid = get_uuid(inputdata['segmentation_config']['distributed_virtual_switch_name'], auth_header, **kwargs)
	# if uuid:
	# 	print(f"Vcenter {inputdata['segmentation_config']['distributed_virtual_switch_name']}, is already added, skipping...")
	# 	return {}

	target_url = kwargs["url"] + "hosts/vswitches"
	host_uuid = hosts.get_host_uuid_by_hostname_and_vsphere(
		inputdata['segmentation_config']['host'],
		inputdata['segmentation_config']['vcenter']['host'],
		auth_header,
		**kwargs)

	host_nic_uuid_list = hosts.list_hostnic_uuid_by_nicname_hostname_and_vsphere(

		inputdata['segmentation_config']['vm_nics'],
		inputdata['segmentation_config']['host'],
		inputdata['segmentation_config']['vcenter']['host'],
		auth_header,
		**kwargs)

	vm_nic_uuid_list = hosts.list_vmnic_uuid_by_vmnamelist_hostname_and_vsphere(
		inputdata['segmentation_config']['test_vms'],
		inputdata['segmentation_config']['host'],
		inputdata['segmentation_config']['vcenter']['host'],
		auth_header,
		**kwargs)

	data = {
        "name": inputdata['segmentation_config']['distributed_virtual_switch_name'],
        "hosts":[{
            "host_uuid": host_uuid,
            "host_nic_uuids":host_nic_uuid_list
		}],
        "pvlans":[{
            "primary_vlan":int(inputdata['segmentation_config']['primary_vlan']),
            "primary_vlan_vnic_uuids":[],
            "isolated_vlan":{
                "vlan":int(inputdata['segmentation_config']['isolated_vlan']),
                "vnic_uuids": vm_nic_uuid_list
            }
        }],
        "portgroup_name_prefix": inputdata['segmentation_config']['portgroup_name_prefix'],
        "lags":[]
    }

	response = kwargs["s"].post(target_url, json=data, headers=auth_header, verify=False)
	if response.status_code not in [200]:
		logging.warning("FAIL: create vswitch failed with status code %d: %s" % (response.status_code, response.text))
		exit(-1)
	else:
		logging.info("SUCCESS: create vswitch succeeded")
		output = response.json()
		return output


def get_uuid(name, auth_header, **kwargs):
	vswitch_dict = get_all(auth_header, **kwargs)
	for vswitch in vswitch_dict:
		if vswitch["name"].casefold() == name.casefold():
			return vswitch["uuid"]
	return ""


def get_all(auth_header, **kwargs):
	target_url = kwargs["url"] + "hosts/vswitches"
	response = kwargs["s"].get(target_url, headers=auth_header, verify=False)
	if response.status_code not in [200]:
		logging.warning("FAIL: get_all vswitches failed with status code %d: %s" % (response.status_code, response.text))
		exit(-1)
	else:
		logging.info("SUCCESS: get_all vswitches succeeded")
		output = response.json()
		return output['result']