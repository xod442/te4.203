#!/usr/bin/env python3

from requests.packages.urllib3.exceptions import InsecureRequestWarning
import urllib3
import requests
import os
import sys
import logging
import json
import pyafc.fabric as fabric

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.basicConfig(level=logging.INFO)


def get_vsx(auth_header, **kwargs):
	target_url = kwargs["url"] + "fabrics'vsx"
	# print("Target_url: " + target_url)
	response = kwargs["s"].get(target_url, headers=auth_header, verify=False)
	if response.status_code not in [200]:
		logging.warning("FAIL: get_vsx failed with status code %d: %s" % (response.status_code, response.text))
		exit(-1)
	else:
		logging.info("SUCCESS: get_vsx succeeded")
		output = response.json()
		return output['result']


def create_vsxes(fabric_uuid, auth_header, name_prefix="myVSXPair", description="MyVsxPair",
				 mac_range_lower="00:00:00:01:02:00", mac_range_upper="00:00:00:01:02:ff", keepalive_mode="routed",
				 keepalive_ip_pool="192.168.10.0", keepalive_ip_prefix=24, svi_vlan=200, **kwargs):
	target_url = kwargs["url"] + f"fabrics/{fabric_uuid}/vsxes"
	print("Target_url: " + target_url)

	data = {
		"fabric_uuid": fabric_uuid,
		"isl_timer_configurations": {
			"hold_time": 0,
			"hello_interval": 1,
			"peer_detect_interval": 300,
			"timeout": 20
		},
		"keep_alive_timers_configurations": {
			"hello_interval": 1,
			"dead_interval": 20
		},
		"keepalive_ip_pool_range":{},
		"system_mac_range":{},
		"keep_alive_udp_port": 7678,
		"linkup_delay_timer": 0,
		"qos_trust": "cos",
		"health": {},
		"split_recovery_disable": True
	}

	if name_prefix:
		data['name_prefix'] = name_prefix
	if description:
		data['description'] = description
	if keepalive_ip_pool:
		data['keepalive_ip_pool_range']['address'] = keepalive_ip_pool
	if keepalive_ip_prefix:
		data['keepalive_ip_pool_range']['prefix_length'] = keepalive_ip_prefix
	if mac_range_lower:
		data['system_mac_range']['lower'] = mac_range_lower
	if mac_range_upper:
		data['system_mac_range']['upper'] = mac_range_upper
	if keepalive_mode:
		data['keep_alive_interface_mode'] = keepalive_mode
	if svi_vlan:
		data['svi_vlan'] = svi_vlan

	# post_data = json.dumps(data, sort_keys=True, indent=4)

	response = kwargs["s"].post(target_url, json=data, headers=auth_header, verify=False)
	if response.status_code not in [200]:
		logging.warning("FAIL: create_vsxes failed with status code %d: %s" % (response.status_code, response.text))
		exit(-1)
	else:
		logging.info("SUCCESS: create_vsxes succeeded")
		output = response.json()
		return output['result']


def delete_all_vsx_pairs(fabric_name, auth_header, **kwargs):
	fabric_uuid = fabric.get_fabrics_uuid(fabric_name, auth_header, **kwargs)

	target_url = kwargs["url"] + f"fabrics/{fabric_uuid}/vsx"
	# print("Target_url: " + target_url)
	response = kwargs["s"].delete(target_url, headers=auth_header, verify=False)
	if response.status_code not in [200]:
		logging.warning("FAIL: delete_all_vsx_pairs failed with status code %d: %s" % (response.status_code, response.text))
		exit(-1)
	else:
		logging.info("SUCCESS: delete_all_vsx_pairs succeeded")
		output = response.json()
		return output

def get_all(fabric_uuid, auth_header, **kwargs):
	target_url = kwargs["url"] + f"fabrics/{fabric_uuid}/vsx"
	# print("Target_url: " + target_url)
	response = kwargs["s"].get(target_url, headers=auth_header, verify=False)
	if response.status_code not in [200]:
		logging.warning("FAIL: get_all_fabrics failed with status code %d: %s" % (response.status_code, response.text))
		exit(-1)
	else:
		logging.info("SUCCESS: get_all VSX succeeded")
		output = response.json()
		return output['result']

def get_uuid(fabric_uuid, vsx_name,auth_header, **kwargs):
	vsx_list = get_all(fabric_uuid, auth_header, **kwargs)
	uuid = ""
	for vsx in vsx_list:
		if vsx["name"].casefold() == vsx_name.casefold():
			uuid = vsx["uuid"]
	return uuid
