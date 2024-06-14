#!/usr/bin/env python3

from requests.packages.urllib3.exceptions import InsecureRequestWarning
import urllib3
import logging

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.basicConfig(level=logging.INFO)


def create(name,
		   endpoints_ipv4_range,
		   auth_header,
		   type="layer3",
		   sub_type="ip_address",
		   endpoints_type="endpoint_group_endpoint_ip",
		   description="",
		   **kwargs):

	uuid = get_uuid(name, auth_header, **kwargs)
	if uuid:
		print(f"Endpoint group: {name}, Already exist. Skipping...")
		return {}

	target_url = kwargs["url"] + "endpoint_groups"
	data = {
		"name": name,
	    "description": description,
	    "type": type,
	    "sub_type": sub_type,
	    "endpoints": [
			{
				"ipv4_range": endpoints_ipv4_range,
				"type": endpoints_type
			}
		]
	}

	response = kwargs["s"].post(target_url, json=data, headers=auth_header, verify=False)
	if response.status_code not in [200]:
		logging.warning("FAIL: create endpoint_groups failed with status code %d: %s" % (response.status_code, response.text))
		exit(-1)
	else:
		logging.info("SUCCESS: create endpoint_groups succeeded")
		output = response.json()
		return output


def delete(name, auth_header, **kwargs):
	uuid = get_uuid(name, auth_header, **kwargs)
	if uuid:
		target_url = kwargs["url"] + "endpoint_groups/{}".format(uuid)
		response = kwargs["s"].delete(target_url, headers=auth_header, verify=False)
		if response.status_code not in [200]:
			logging.warning("FAIL: delete endpoint_groups failed with status code %d: %s" % (response.status_code, response.text))
			exit(-1)
		else:
			logging.info("SUCCESS: delete endpoint_groups succeeded")
			output = response.json()
			return output


def get_uuid(name, auth_header, **kwargs):
	endpoint_group_dict = get_all(auth_header, **kwargs)
	uuid = ""
	for endpoint_group in endpoint_group_dict:
		if endpoint_group["name"].casefold() == name.casefold():
			uuid = endpoint_group["uuid"]
	return uuid

def convert_name_list_to_uuid_list(name_list, auth_header, **kwargs):
	endpoint_group_dict = get_all(auth_header, **kwargs)
	uuid_list = []
	for name in name_list:
		for endpoint_group in endpoint_group_dict:
			if endpoint_group["name"].casefold() == name.casefold():
				uuid_list.append(endpoint_group["uuid"])
				break
	return uuid_list

def get_all(auth_header, **kwargs):
	target_url = kwargs["url"] + "endpoint_groups"
	response = kwargs["s"].get(target_url, headers=auth_header, verify=False)
	if response.status_code not in [200]:
		logging.warning("FAIL: get_all endpoint_groups failed with status code %d: %s" % (response.status_code, response.text))
		exit(-1)
	else:
		logging.info("SUCCESS: get_all endpoint_groups succeeded")
		output = response.json()
		return output['result']