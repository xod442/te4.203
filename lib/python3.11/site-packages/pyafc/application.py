#!/usr/bin/env python3

from requests.packages.urllib3.exceptions import InsecureRequestWarning
import urllib3
import logging

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.basicConfig(level=logging.INFO)


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
	target_url = kwargs["url"] + "applications"
	response = kwargs["s"].get(target_url, headers=auth_header, verify=False)
	if response.status_code not in [200]:
		logging.warning("FAIL: get_all applications failed with status code %d: %s" % (response.status_code, response.text))
		exit(-1)
	else:
		logging.info("SUCCESS: get_all applications succeeded")
		output = response.json()
		return output['result']