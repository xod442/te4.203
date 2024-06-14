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


def create_leaf_spine(fabric_uuid, auth_header, name_prefix="MyLS", description="MySpineLeaf",
					  leaf_spine_ip_pool_range_address="192.168.1.0", leaf_spine_ip_pool_range_prefix_length=24, **kwargs):
	target_url = kwargs["url"] + f"fabrics/{fabric_uuid}/leaf_spine_workflow"
	print("Target_url: " + target_url)

	data = {
		"fabric_uuid": fabric_uuid,
		"description": description,
		"qos_trust": "cos",
		"leaf_spine_ip_pool_range": {
			"address": leaf_spine_ip_pool_range_address,
			"prefix_length": leaf_spine_ip_pool_range_prefix_length
		},
		"name_prefix": name_prefix
	}

	response = kwargs["s"].post(target_url, json=data, headers=auth_header, verify=False)
	if response.status_code not in [200]:
		logging.warning("FAIL: create_leaf_spine failed with status code %d: %s" % (response.status_code, response.text))
		exit(-1)
	else:
		logging.info("SUCCESS: create_leaf_spine succeeded")
		output = response.json()
		return output['result']


def delete_all(auth_header, **kwargs):
	target_url = kwargs["url"] + "fabrics/leaf_spine"
	# print("Target_url: " + target_url)
	response = kwargs["s"].delete(target_url, headers=auth_header, verify=False)
	if response.status_code not in [200]:
		logging.warning("FAIL: delete_all leaf spine failed with status code %d: %s" % (response.status_code, response.text))
		exit(-1)
	else:
		logging.info("SUCCESS: delete_all leaf spine succeeded")
		output = response.json()
		return output
