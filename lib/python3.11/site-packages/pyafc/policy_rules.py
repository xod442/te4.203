#!/usr/bin/env python3

from requests.packages.urllib3.exceptions import InsecureRequestWarning
import pyafc.endpoint_group as endpoint_group
import pyafc.application as application
import urllib3
import logging

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.basicConfig(level=logging.INFO)


def create(data, auth_header, **kwargs):

	uuid = get_uuid(data['name'], auth_header, **kwargs)
	if uuid:
		print(f"Rule: {data['name']}, Already exist. Skipping...")
		return {}

	target_url = kwargs["url"] + "rules"
	data["source_endpoint_groups"] = endpoint_group.convert_name_list_to_uuid_list(data["source_endpoint_groups"],auth_header,**kwargs)
	data["destination_endpoint_groups"] = endpoint_group.convert_name_list_to_uuid_list(data["destination_endpoint_groups"],auth_header,**kwargs)
	data["applications"] = application.convert_name_list_to_uuid_list(data["applications"],auth_header,**kwargs)

	response = kwargs["s"].post(target_url, json=data, headers=auth_header, verify=False)
	if response.status_code not in [200]:
		logging.warning("FAIL: create policy rules failed with status code %d: %s" % (response.status_code, response.text))
		exit(-1)
	else:
		logging.info("SUCCESS: create policy_rules succeeded")
		output = response.json()
		return output


def delete(name, auth_header, **kwargs):
	uuid = get_uuid(name, auth_header, **kwargs)
	if not uuid:
		return {}

	target_url = kwargs["url"] + "rules/{}".format(uuid)
	response = kwargs["s"].delete(target_url, headers=auth_header, verify=False)
	if response.status_code not in [200]:
		logging.warning("FAIL: delete rules failed with status code %d: %s" % (response.status_code, response.text))
		exit(-1)
	else:
		logging.info("SUCCESS: delete rules succeeded")
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
	rules_dict = get_all(auth_header, **kwargs)
	uuid_list = []
	for name in name_list:
		for rule in rules_dict:
			if rule["name"].casefold() == name.casefold():
				uuid_list.append(rule["uuid"])
				break
	return uuid_list


def get_all(auth_header, **kwargs):
	target_url = kwargs["url"] + "rules"
	response = kwargs["s"].get(target_url, headers=auth_header, verify=False)
	if response.status_code not in [200]:
		logging.warning("FAIL: get_all rules failed with status code %d: %s" % (response.status_code, response.text))
		exit(-1)
	else:
		logging.info("SUCCESS: get_all rules succeeded")
		output = response.json()
		return output['result']