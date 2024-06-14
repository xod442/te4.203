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


def create_bgp(switch_uuids, fabric_uuid, name_prefix,description,vni_base,vlans,upper,lower,rt_type,administrative_number,auth_header,**kwargs):
	target_url = kwargs["url"] + "evpn"
	# print("Target_url: " + target_url)
	
	data = {
		"switches": switch_uuids,
		"fabric_uuid": fabric_uuid,
		"name_prefix": name_prfix,
		"description": description,
		"vni_base": vni_base,
		"vlans": vlans,
		"system_mac_range['upper']": upper,
		"system_mac_range['lower']": lower,
		"rt_type": "NN:VNI",
		"administrative_number"
	}
	# post_data = json.dumps(data, sort_keys=True, indent=4)

	response = kwargs["s"].post(target_url, json=data, headers=auth_header, verify=False)
	if response.status_code not in [200]:
		logging.warning("FAIL: create_evpnss failed with status code %d: %s" % (response.status_code, response.text))
		exit(-1)
	else:
		logging.info("SUCCESS: discover_switches succeeded")
		output = response.json()
		return output
