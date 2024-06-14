#!/usr/bin/env python3

from requests.packages.urllib3.exceptions import InsecureRequestWarning
import urllib3
import requests
import os
import sys
import logging
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.basicConfig(level=logging.INFO)


def get_all_fabrics(auth_header, **kwargs):
	target_url = kwargs["url"] + "fabrics"
	# print("Target_url: " + target_url)
	response = kwargs["s"].get(target_url, headers=auth_header, verify=False)
	if response.status_code not in [200]:
		logging.warning("FAIL: get_all_fabrics failed with status code %d: %s" % (response.status_code, response.text))
		exit(-1)
	else:
		logging.info("SUCCESS: get_all_fabrics succeeded")
		output = response.json()
		return output['result']


def get_fabric(fabric_name, auth_header, **kwargs):
	uuid = get_fabrics_uuid(fabric_name, auth_header, **kwargs)
	target_url = kwargs["url"] + "fabrics/{}".format(uuid)
	# print("Target_url: " + target_url)
	response = kwargs["s"].get(target_url, headers=auth_header, verify=False)
	if response.status_code not in [200]:
		logging.warning("FAIL: get_fabric failed with status code %d: %s" % (response.status_code, response.text))
		exit(-1)
	else:
		logging.info("SUCCESS: get_fabric succeeded")
		output = response.json()
		return output['result']


def create_fabric(fabric_name, auth_header, timezone="America/Los_Angeles", description="MyFabic", fabric_pass=None, **kwargs):
	target_url = kwargs["url"] + "fabrics?fabric_class=Leaf-Spine"
	# print("Target_url: " + target_url)

	data = {
		"name": fabric_name
	}
	if timezone:
		data['timezone'] = timezone
	if description:
		data['description'] = description
	if fabric_pass:
		data['password'] = fabric_pass

	# post_data = json.dumps(data, sort_keys=True, indent=4)

	response = kwargs["s"].post(target_url, json=data, headers=auth_header, verify=False)
	if response.status_code not in [200]:
		logging.warning("FAIL: create_fabric failed with status code %d: %s" % (response.status_code, response.text))
		exit(-1)
	else:
		logging.info("SUCCESS: create_fabric succeeded")
		output = response.json()
		return output


def delete_fabric(fabric_name, auth_header, **kwargs):
	uuid = get_fabrics_uuid(fabric_name, auth_header, **kwargs)
	target_url = kwargs["url"] + "fabrics/{}".format(uuid)
	# print("Target_url: " + target_url)
	response = kwargs["s"].delete(target_url, headers=auth_header, verify=False)
	if response.status_code not in [200]:
		logging.warning("FAIL: delete_fabric failed with status code %d: %s" % (response.status_code, response.text))
		exit(-1)
	else:
		logging.info("SUCCESS: delete_fabric succeeded")
		output = response.json()
		return output


def get_fabrics_uuid(fabric_name, auth_header, **kwargs):
	fabric_dict = get_all_fabrics(auth_header, **kwargs)
	uuid = ""
	for fabric in fabric_dict:
		if fabric["name"].casefold() == fabric_name.casefold():
			uuid = fabric["uuid"]
	return uuid
