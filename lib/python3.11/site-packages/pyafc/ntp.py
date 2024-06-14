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


def get_all_ntps(auth_header, **kwargs):
	target_url = kwargs["url"] + "ntp_client_configurations"
	# print("Target_url: " + target_url)
	response = kwargs["s"].get(target_url, headers=auth_header, verify=False)
	if response.status_code not in [200]:
		logging.warning("FAIL: get_all_ntps failed with status code %d: %s" % (response.status_code, response.text))
		exit(-1)
	else:
		logging.info("SUCCESS: get_all_ntps succeeded")
		output = response.json()
		return output['result']


def get_ntp(ntp_name, auth_header, **kwargs):
	uuid = get_ntps_uuid(ntp_name, auth_header, **kwargs)
	target_url = kwargs["url"] + "ntp_client_configurations/{}".format(uuid)
	# print("Target_url: " + target_url)
	response = kwargs["s"].get(target_url, headers=auth_header, verify=False)
	if response.status_code not in [200]:
		logging.warning("FAIL: get_ntp failed with status code %d: %s" % (response.status_code, response.text))
		exit(-1)
	else:
		logging.info("SUCCESS: get_ntp succeeded")
		output = response.json()
		return output['result']


def create_ntp(ntp_name, fabric_uuid_list, server_ip, auth_header, switch_uuids=[], description="", **kwargs):
	target_url = kwargs["url"] + "ntp_client_configurations"
	# print("Target_url: " + target_url)

	data = {
		"name": ntp_name,
		"description": description,
		"fabric_uuids": fabric_uuid_list,
		"switch_uuids": switch_uuids,
		"entry_list":
			[
				{
					"server": server_ip
				}
			]
	}

	# post_data = json.dumps(data, sort_keys=True, indent=4)

	response = kwargs["s"].post(target_url, json=data, headers=auth_header, verify=False)
	if response.status_code not in [200]:
		logging.warning("FAIL: create_ntp failed with status code %d: %s" % (response.status_code, response.text))
		exit(-1)
	else:
		logging.info("SUCCESS: create_ntp succeeded")
		output = response.json()
		return output


def delete_ntp(ntp_name, auth_header, **kwargs):
	uuid = get_ntps_uuid(ntp_name, auth_header, **kwargs)
	target_url = kwargs["url"] + "ntp_client_configurations/{}".format(uuid)
	# print("Target_url: " + target_url)
	response = kwargs["s"].delete(target_url, headers=auth_header, verify=False)
	if response.status_code not in [200]:
		logging.warning("FAIL: delete_ntp failed with status code %d: %s" % (response.status_code, response.text))
		exit(-1)
	else:
		logging.info("SUCCESS: delete_ntp succeeded")
		output = response.json()
		return output


def get_ntps_uuid(ntp_name, auth_header, **kwargs):
	ntp_dict = get_all_ntps(auth_header, **kwargs)
	uuid = ""
	for ntp in ntp_dict:
		if ntp["name"].casefold() == ntp_name.casefold():
			uuid = ntp["uuid"]
	return uuid

