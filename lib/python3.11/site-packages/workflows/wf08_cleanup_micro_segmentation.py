#!/usr/bin/env python3

from requests.packages.urllib3.exceptions import InsecureRequestWarning
import urllib3
import requests
import os
import sys
import logging
import json
sys.path.append('../') # Needed to run workfile directly form this repository
import pyafc.session as session
import pyafc.policy_rules as policy_rules
import pyafc.policy as policy

import pyafc.devices as devices
import pyafc.fabric as fabric
import pyafc.vrfs as vrfs
import pyafc.endpoint_group as endpoint_group
import pyafc.vcenter as vcenter
import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.basicConfig(level=logging.INFO)


def main():
	# Take input from JSON file
	data = json.loads(open(sys.argv[1], "r").read())  # Combined input
	print(datetime.datetime.now())
	fabric_name = data['fabric_name']
	vrf_name = data['segmentation_config']['vrf_name']
	afc_ip = data['afc_ip']
	username = data['username']
	password = data['password']
	auth_header = {}
	os.environ['no_proxy'] = afc_ip
	os.environ['NO_PROXY'] = afc_ip
	base_url = "https://{0}/api/v1/".format(afc_ip)


	try:
		login_session, auth_header = session.login(base_url, username, password)
		session_dict = dict(s=login_session, url=base_url)

		print("Deleting All IP interfaces for VRF named {}".format(fabric_name))
		vrfs.delete_all_ip_interfaces(vrf_name, auth_header, **session_dict)


		print("Deleting VRF named {}".format(fabric_name))
		vrfs.delete_vrf(vrf_name, auth_header, **session_dict)

		print("Delete policy...")
		policy.delete(
			data["segmentation_config"]["policy"]["policy"]["name"],
			auth_header,
			**session_dict)
		print(f"Deleted policy named {data['segmentation_config']['policy']['policy']['name']}")

		print("Delete policy rules...")
		for rule in data["segmentation_config"]["policy"]["rules"]:
			policy_rules.delete(
				rule["name"],
				auth_header,
				**session_dict)
			print(f"Deleted policy rule named {rule['name']}")

		print(
			"Deleting Endpoint group named {}".format(data["segmentation_config"]["policy"]["endpoint_group"]["name"]))
		endpoint_group.delete(
			data["segmentation_config"]["policy"]["endpoint_group"]["name"],
			auth_header,
			**session_dict)

		print("Delete Vcenter...")
		add_vcenter_result = vcenter.remove(
			data["segmentation_config"]["vcenter"]['host'],
			auth_header,
			**session_dict)
		print(f"Add vcenter {data['segmentation_config']['vcenter']['name']} result is: {add_vcenter_result}")

	# print("Deleting Fabric named {}".format(fabric_name))
		# fabric.delete_fabric(fabric_name, auth_header, **session_dict)


	except Exception as error:
		print('Ran into exception: {}. Logging out...'.format(error))
	session.logout(auth_header, **session_dict)


if __name__ == '__main__':
	main()