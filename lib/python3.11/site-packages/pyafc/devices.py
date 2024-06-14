#!/usr/bin/env python3

from requests.packages.urllib3.exceptions import InsecureRequestWarning
import urllib3
import logging

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.basicConfig(level=logging.INFO)


def discover_switches(switch_list, auth_header, admin_pwd="admin", afc_admin_pwd="admin", switch_types=["Aruba"], **kwargs):
	target_url = kwargs["url"] + "switches/discover"
	data = {
		"switches": switch_list,
		"admin_passwd": admin_pwd,
		"afc_admin_passwd": afc_admin_pwd
	}
	

	response = kwargs["s"].post(target_url, json=data, headers=auth_header, verify=False)
	if response.status_code not in [200]:
		logging.warning("FAIL: discover_switches failed with status code %d: %s" % (response.status_code, response.text))
		exit(-1)
	else:
		logging.info("SUCCESS: discover_switches succeeded")
		output = response.json()
		return output


def add_switches_to_fabric(switch_list, auth_header, role, fabric_uuid, **kwargs):
	all_switch_list = get_all_switches(auth_header, **kwargs)
	specific_switch_uuids = []

	for significant_switch in switch_list:
		for switch in all_switch_list:
			if significant_switch == switch['ip_address'] and not switch['fabric_uuid']:
				specific_switch_uuids.append(switch['uuid'])
				print("Adding {} to fabric.".format(switch['ip_address']))

	target_url = kwargs["url"] + "switches"
	print("UUID LIST:============")
	print(specific_switch_uuids)
	patch_data = [
		{
			"uuids": specific_switch_uuids,
			"patch": [
				{
					"path": "/fabric_uuid",
					"value": fabric_uuid,
					"op": "replace"
				},
				{
					"path": "/role",
					"value": role,
					"op": "replace"
				}
			]
		}
	]

	response = kwargs["s"].patch(target_url, json=patch_data, headers=auth_header, verify=False)
	if response.status_code not in [200]:
		logging.warning("FAIL: adding %s switches to fabric failed with status code %d: %s" % (role, response.status_code, response.text))
		exit(-1)
	else:
		logging.info("SUCCESS: adding switches to fabric succeeded")
		output = response.json()
		return output


def delete_switches_from_afc(switch_list, auth_header,  **kwargs):
	target_url = kwargs["url"] + "switches/"
	uuid_dict = get_switches_uuids(switch_list, auth_header, **kwargs)
	output = {}
	for switch in uuid_dict:
		if switch in switch_list:
			switch_url = target_url + uuid_dict[switch]
			response = kwargs["s"].delete(switch_url, headers=auth_header, verify=False)
			if response.status_code not in [200]:
				logging.warning("FAIL: delete_switches_from_afc failed with status code %d: %s" % (response.status_code, response.text))
				exit(-1)
			else:
				logging.info("Deleted switch " + switch + " from AFC")
				output[switch] = response.json()

	logging.info("SUCCESS: delete_switches_from_afc succeeded")
	return output


def get_all_switches(auth_header, **kwargs):
	target_url = kwargs["url"] + "switches"
	response = kwargs["s"].get(target_url, headers=auth_header, verify=False)
	if response.status_code not in [200]:
		logging.warning("FAIL: get_all_switches failed with status code %d: %s" % (response.status_code, response.text))
		exit(-1)
	else:
		logging.info("SUCCESS: get_all_switches succeeded")
		output = response.json()
		return output['result']


def get_switches_uuids(ip_list, auth_header, **kwargs):
	uuid_dict = {}
	target_url = kwargs["url"] + "switches"
	response = kwargs["s"].get(target_url, headers=auth_header, verify=False)
	if response.status_code not in [200]:
		logging.warning("FAIL: get_switches_uuids failed with status code %d: %s" % (response.status_code, response.text))
		exit(-1)
	else:
		output = response.json()
		# print(f"switch uuids: {output['result']}")
		for switch in output['result']:
			if switch['ip_address'] in ip_list:
				uuid_dict[switch['ip_address']] = switch['uuid']
			if 'hostname' in switch and switch['hostname'] in ip_list:
				uuid_dict[switch['hostname']] = switch['uuid']
		logging.info("SUCCESS: get_switches_uuids succeeded")
		return uuid_dict
