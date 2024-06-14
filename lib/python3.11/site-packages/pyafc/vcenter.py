#!/usr/bin/env python3

from requests.packages.urllib3.exceptions import InsecureRequestWarning
import urllib3
import logging

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.basicConfig(level=logging.INFO)


def add(data, auth_header, **kwargs):
	target_url = kwargs["url"] + "vmware/vcenters"
	uuid = get_uuid_by_vsphere_hostname(data['host'], auth_header, **kwargs)
	if uuid:
		print(f"Vcenter {data['name']}, is already added, skipping...")
		return {}
	response = kwargs["s"].post(target_url, json=data, headers=auth_header, verify=False)
	if response.status_code not in [200]:
		logging.warning("FAIL: Add vcenter failed with status code %d: %s" % (response.status_code, response.text))
		exit(-1)
	else:
		logging.info("SUCCESS: Add vcenter succeeded")
		output = response.json()
		return output


def remove(name, auth_header, **kwargs):
	uuid = get_uuid_by_vsphere_hostname(name, auth_header, **kwargs)
	if not uuid:
		print(f"Vcenter {name}, is already removed, skipping...")
		return {}
	target_url = kwargs["url"] + "vmware/vcenters/{}".format(uuid)
	response = kwargs["s"].delete(target_url, headers=auth_header, verify=False)
	if response.status_code not in [200, 202]:
		logging.warning("FAIL: delete vcenter failed with status code %d: %s" % (response.status_code, response.text))
		exit(-1)
	else:
		logging.info("SUCCESS: delete vcenter succeeded")
		output = response.json()
		return output


def get_uuid_by_vsphere_hostname(vsphere_name, auth_header, **kwargs):
	host_dict = get_all(auth_header, **kwargs)
	for host in host_dict:
		if host["host"].casefold() == vsphere_name.casefold():
			return host['uuid']
	return ""


def get_all(auth_header, **kwargs):
	target_url = kwargs["url"] + "vmware/vcenters"
	response = kwargs["s"].get(target_url, headers=auth_header, verify=False)
	if response.status_code not in [200]:
		logging.warning("FAIL: get_all vmware centers failed with status code %d: %s" % (response.status_code, response.text))
		exit(-1)
	else:
		logging.info("SUCCESS: get_all vmware centers succeeded")
		output = response.json()
		return output['result']