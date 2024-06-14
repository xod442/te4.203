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


def get_all_evpn(auth_header, **kwargs):
	target_url = kwargs["url"] + "evpn"
	# print("Target_url: " + target_url)
	response = kwargs["s"].get(target_url, headers=auth_header, verify=False)
	if response.status_code not in [200]:
		logging.warning("FAIL: get_all_evpn failed with status code %d: %s" % (response.status_code, response.text))
		exit(-1)
	else:
		logging.info("SUCCESS: get_all_evpn succeeded")
		output = response.json()
		return output['result']


def get_evpn(evpn_name, auth_header, **kwargs):
	uuid = get_evpn_uuid(evpn_name, auth_header, **kwargs)
	target_url = kwargs["url"] + "evpn/{}".format(uuid)
	# print("Target_url: " + target_url)
	response = kwargs["s"].get(target_url, headers=auth_header, verify=False)
	if response.status_code not in [200]:
		logging.warning("FAIL: get_evpn failed with status code %d: %s" % (response.status_code, response.text))
		exit(-1)
	else:
		logging.info("SUCCESS: get_evpn succeeded")
		output = response.json()
		return output['result']


def create_evpn(
		name_prefix,
		fabric_uuid,
		auth_header,
		switch_uuids=[],
		mac_range_lower="00:00:00:01:02:00",
		mac_range_upper="00:00:00:01:02:ff",
		vlans="5, 20-50, 70",
		description="L2 VPN 01",
		rt_type="ASN:NN",
		administrative_number=1000,
		vni=1, **kwargs):
	target_url = kwargs["url"] + "evpn"
	# print("Target_url: " + target_url)

	data = {
		"name_prefix": name_prefix,
		"description": description,
		"vni_base": vni,
		"vlans": vlans,
		"fabric_uuid": fabric_uuid,
		"switch_uuids": switch_uuids,
		"system_mac_range": {
			"lower": mac_range_lower,
			"upper": mac_range_upper
		},
		"rt_type": rt_type,
		# "administrative_number": administrative_number
	}

	if rt_type not in "AUTO":
		data['administrative_number'] = administrative_number

	response = kwargs["s"].post(target_url, json=data, headers=auth_header, verify=False)
	if response.status_code not in [200]:
		logging.warning("FAIL: create_evpn failed with status code %d: %s" % (response.status_code, response.text))
		exit(-1)
	else:
		logging.info("SUCCESS: create_evpn succeeded")
		output = response.json()
		return output['result']


def delete_evpn(evpn_name, auth_header, **kwargs):
	uuid = get_evpn_uuid(evpn_name, auth_header, **kwargs)

	target_url = kwargs["url"] + "evpn/{}".format(uuid)
	# print("Target_url: " + target_url)
	response = kwargs["s"].delete(target_url, headers=auth_header, verify=False)
	if response.status_code not in [200]:
		logging.warning("FAIL: delete_evpn failed with status code %d: %s" % (response.status_code, response.text))
		exit(-1)
	else:
		logging.info("SUCCESS: delete_evpn succeeded")
		output = response.json()
		return output


def get_evpn_uuid(evpn_name, auth_header, **kwargs):
	evpn_dict = get_all_evpn(auth_header, **kwargs)
	uuid = ""
	for evpn in evpn_dict:
		if evpn["name"].casefold() == evpn_name.casefold():
			uuid = evpn["uuid"]
	return uuid

