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

def create_overlay(
		vrf_uuid,
		auth_header,
		name="MyUnderlay",
		description="MyOverlay",
		bgp_type="internal",
		spine_ids=[ "cce09ea3-8079-4813-b8d2-8826df8fefd8","d3cb8e4c-da44-4858-8846-f97bf792509c"],
		spine_leaf_asn="65101",
		ipv4_address="192.168.12.0",
		ipv4_prefix_length=24,
		**kwargs):
	target_url = kwargs["url"] + f"vrfs/{vrf_uuid}/overlay"
	print("Target_url: " + target_url)

	data = {
		"name": name,
		"description": description,
		"bgp_type": bgp_type,
		"ebgp": {
			"asn_type": "DUAL",
			"dual_asn": {
				"spine_asn": "65000.0",
				"leaf_asn": "65001.0"
			},
			"multi_asn": {
				"starting_sl_asn": "65000.0",
				"starting_bdr_asn": "65100.0"
			},
			"auth_password": "string"
		},
		"ibgp": {
			"spine_leaf_asn": spine_leaf_asn,
			"rr_server": spine_ids,
			"auth_password": "",
			"spine_group_name": "",
			"leaf_group_name": ""
		},
		"keepalive_timer": 60,
		"holddown_timer": 180,
		"force_timers_update": True,
		"ipv4_address": {
			"address": ipv4_address,
			"prefix_length": ipv4_prefix_length
		}
	}

	response = kwargs["s"].post(target_url, json=data, headers=auth_header, verify=False)
	if response.status_code not in [200]:
		logging.warning("FAIL: create_overlay failed with status code %d: %s" % (response.status_code, response.text))
		exit(-1)
	else:
		logging.info("SUCCESS: create_overlay succeeded")
		output = response.json()
		return output['result']
