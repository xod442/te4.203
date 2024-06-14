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


def get_all_dns(auth_header, **kwargs):
	target_url = kwargs["url"] + "dns_client_configurations"
	# print("Target_url: " + target_url)
	response = kwargs["s"].get(target_url, headers=auth_header, verify=False)
	if response.status_code not in [200]:
		logging.warning("FAIL: get_all_dns failed with status code %d: %s" % (response.status_code, response.text))
		exit(-1)
	else:
		logging.info("SUCCESS: get_all_dns succeeded")
		output = response.json()
		return output['result']


def get_dns(dns_name, auth_header, **kwargs):
	uuid = get_dns_uuid(dns_name, auth_header, **kwargs)
	target_url = kwargs["url"] + "dns_client_configurations/{}".format(uuid)
	# print("Target_url: " + target_url)
	response = kwargs["s"].get(target_url, headers=auth_header, verify=False)
	if response.status_code not in [200]:
		logging.warning("FAIL: get_dns failed with status code %d: %s" % (response.status_code, response.text))
		exit(-1)
	else:
		logging.info("SUCCESS: get_dns succeeded")
		output = response.json()
		return output['result']


def create_dns(dns_afc_name, fabric_uuid_list, domain_name, name_server_list, auth_header,
				domain_list=[], switch_uuids=[], description="", management=False, **kwargs):
	target_url = kwargs["url"] + "dns_client_configurations"
	# print("Target_url: " + target_url)

	data = {
		"name": dns_afc_name,
		"description": description,
		"domain_name": domain_name,
		"name_servers": name_server_list,
		"domain_list": domain_list,
		"management_software": management,
		"fabric_uuids": fabric_uuid_list,
		"switch_uuids": switch_uuids
	}

	response = kwargs["s"].post(target_url, json=data, headers=auth_header, verify=False)
	if response.status_code not in [200]:
		logging.warning("FAIL: create_dns failed with status code %d: %s" % (response.status_code, response.text))
		exit(-1)
	else:
		logging.info("SUCCESS: create_dns succeeded")
		output = response.json()
		return output


def delete_dns(dns_name, auth_header, **kwargs):
	uuid = get_dns_uuid(dns_name, auth_header, **kwargs)

	target_url = kwargs["url"] + "dns_client_configurations/{}".format(uuid)
	response = kwargs["s"].delete(target_url, headers=auth_header, verify=False)
	if response.status_code not in [200]:
		logging.warning("FAIL: delete_dns failed with status code %d: %s" % (response.status_code, response.text))
		exit(-1)
	else:
		logging.info("SUCCESS: delete_dns succeeded")
		output = response.json()
		return output


def get_dns_uuid(dns_name, auth_header, **kwargs):
	dns_dict = get_all_dns(auth_header, **kwargs)
	uuid = ""
	for dns in dns_dict:
		if dns["name"].casefold() == dns_name.casefold():
			uuid = dns["uuid"]
	return uuid

