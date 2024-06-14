#!/usr/bin/env python3

from requests.packages.urllib3.exceptions import InsecureRequestWarning
import urllib3
import os
import sys
import logging
import json
sys.path.append('../') # Needed to run workflow directly from this repository
import pyafc.session as session
import pyafc.fabric as fabric
import pyafc.ports as ports
import pyafc.ssh as ssh
import pyafc.policy as policy
import datetime
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.basicConfig(level=logging.INFO)


def main():
	# Take input from JSON file
	data = json.loads(open(sys.argv[1], "r").read())  # Combined input
	print(datetime.datetime.now())

	fabric_name = data['fabric_name']
	afc_ip = data['afc_ip']
	username = data['username']
	password = data['password']
	os.environ['no_proxy'] = afc_ip
	os.environ['NO_PROXY'] = afc_ip
	base_url = "https://{0}/api/v1/".format(afc_ip)


	microsegmentation_leaf_switch_List = data['segmentation_config']['segmentation_switch']
	print (f"microsegmentation_leaf_switch_List: {microsegmentation_leaf_switch_List}")
	try:
		login_session, auth_header = session.login(base_url, username, password)
		session_dict = dict(s=login_session, url=base_url)

		print("Getting fabric UUID")
		fabric_uuid = fabric.get_fabrics_uuid(fabric_name, auth_header, **session_dict)
		print(f"Fabric UUID: {fabric_uuid}")

		# print("Waiting for 30 seconds...")
		# time.sleep(30)
		print("Validate micro segmentation...")
		print("Validate ports...")
		valid_vlans_exist = ports.validate_vlans(
			[
				data['segmentation_config']['primary_vlan'],
				data['segmentation_config']['isolated_vlan'],
			],
			data['segmentation_config']['segmentation_switch'][0],
			data['segmentation_config']['segmentation_switch_port'][0],
			auth_header,
			**session_dict)

		if valid_vlans_exist:
			print("PASSED: Valid VLANS shows under configuration/port")
		else:
			print("FAILED: Valid VLANS do not show under port, please check config and wait for a few more seconds.")

		print("Validate PVLANs...")
		valid_vlans_exist = ports.validate_pvlans(
			fabric_uuid,
			data['segmentation_config']['vcenter']['name'],
			data['segmentation_config']['segmentation_switch'][0],
			data['segmentation_config']['distributed_virtual_switch_name'],
			data['segmentation_config']['primary_vlan'],
			data['segmentation_config']['isolated_vlan'],
			auth_header,
			**session_dict)

		if valid_vlans_exist:
			print("PASSED: Valid PVLANS shows under configuration/PVLANS")
		else:
			print("FAILED: Valid PVLANS do not show under configuration/PVLANS, please check config and wait for a few more seconds.")

		print("Validate Policy...")
		print("Validate VM test with existing policy...")
		ping_status = ssh.is_ping_ok(
			data['segmentation_config']['test_vms'][0]['ip'],
			data['segmentation_config']['test_vms'][0]['username'],
			data['segmentation_config']['test_vms'][0]['password'],
			data['segmentation_config']['test_vms'][1]['ip_assigned'])
		if ping_status:
			print("PASSED: VM can be pinged with Allow All policy enabled")
		else:
			print("FAILED: VM can not be pinged even with Allow All policy enabled, Please check...")

		print("Validate VM test with disabling AllowAll rule...")
		policy.disable_rule("BlockSSH", "AllowAll", auth_header, **session_dict)
		time.sleep(2)
		ping_status = ssh.is_ping_ok(
			data['segmentation_config']['test_vms'][0]['ip'],
			data['segmentation_config']['test_vms'][0]['username'],
			data['segmentation_config']['test_vms'][0]['password'],
			data['segmentation_config']['test_vms'][1]['ip_assigned'])
		if not ping_status:
			print("PASSED: VM can not be pinged with Allow All policy disabled")
		else:
			print("FAILED: VM can be pinged with Allow All policy disabled")

		print("Validate VM test with disabling AllowAll rule...")
		policy.enable_rule("BlockSSH", "AllowAll", auth_header, **session_dict)
		time.sleep(2)
		ping_status = ssh.is_ping_ok(
			data['segmentation_config']['test_vms'][0]['ip'],
			data['segmentation_config']['test_vms'][0]['username'],
			data['segmentation_config']['test_vms'][0]['password'],
			data['segmentation_config']['test_vms'][1]['ip_assigned'])
		if ping_status:
			print("PASSED: VM can be pinged with Allow All policy enabled")
		else:
			print("FAILED: VM can not be pinged even with Allow All policy enabled, Please check...")

		session.logout(auth_header, **session_dict)
	except Exception as error:
		print('Ran into exception: {}. Logging out...'.format(error))
		# session.logout(auth_header, **session_dict)


if __name__ == '__main__':
	main()