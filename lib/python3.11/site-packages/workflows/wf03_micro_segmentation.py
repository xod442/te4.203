#!/usr/bin/env python3

from requests.packages.urllib3.exceptions import InsecureRequestWarning
import urllib3
import os
import sys
import logging
import json
sys.path.append('../') # Needed to run workflow directly from this repository
import pyafc.session as session
import pyafc.devices as devices
import pyafc.fabric as fabric
import pyafc.vcenter as vcenter
import pyafc.vrfs as vrfs
import pyafc.endpoint_group as endpoint_group
import pyafc.policy_rules as policy_rules
import pyafc.policy as policy
import pyafc.vswitch as vswitch
import datetime
import time

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

	microsegmentation_leaf_switch_List = data["segmentation_config"]['segmentation_switch']
	print (f"microsegmentation_leaf_switch_List: {microsegmentation_leaf_switch_List}")
	try:
		login_session, auth_header = session.login(base_url, username, password)
		session_dict = dict(s=login_session, url=base_url)

		print("Getting fabric UUID")
		fabric_uuid = fabric.get_fabrics_uuid(fabric_name, auth_header, **session_dict)
		print(f"Fabric UUID: {fabric_uuid}")

		print("Add Vcenter...")
		add_vcenter_result = vcenter.add(
			data["segmentation_config"]["vcenter"],
			auth_header,
			**session_dict)
		print(f"Add vcenter {data['segmentation_config']['vcenter']['name']} result is: {add_vcenter_result}")

		print("Creating VRF")
		vrfs.create_vrf(vrf_name, fabric_uuid, auth_header, primary_route_target="65001:101",
						address_family="ipv4_unicast", route_mode="both", max_routes=0, vni=5, **session_dict)


		print("Create VRF IP Interfaces...")
		leaf_switch_dict = devices.get_switches_uuids(microsegmentation_leaf_switch_List, auth_header, **session_dict)
		print(f"leaf_switch_dict: {leaf_switch_dict}")
		leaf_switch_uuid_list = []
		for leaf_switch in leaf_switch_dict:
			leaf_switch_uuid_list.append(leaf_switch_dict[leaf_switch])
		print(f"Leaf switch list: {leaf_switch_uuid_list}")

		create_vrf_ip_interface_result = vrfs.create_ip_interfaces(
			data["segmentation_config"]["vrf_ip_interface_config"]["vrf_name"],
			leaf_switch_uuid_list[0],
			auth_header,
			name=data["segmentation_config"]["vrf_ip_interface_config"]["name"],
			active_gateway_ipv4_address=data["segmentation_config"]["vrf_ip_interface_config"]["active_gateway_ipv4_address"],
			active_gateway_mac_address=data["segmentation_config"]["vrf_ip_interface_config"]["active_gateway_mac_address"],
			ipv4_primary_addres_address=data["segmentation_config"]["vrf_ip_interface_config"]["ipv4_primary_addres_address"],
			ipv4_primary_address_prefix_length=data["segmentation_config"]["vrf_ip_interface_config"]["ipv4_primary_address_prefix_length"],
			if_type=data["segmentation_config"]["vrf_ip_interface_config"]["if_type"],
			description = data["segmentation_config"]["vrf_ip_interface_config"]["description"],
			vlan = data["segmentation_config"]["vrf_ip_interface_config"]["vlan"],
			ipv4_secondary_address = data["segmentation_config"]["vrf_ip_interface_config"]["ipv4_secondary_address"],
			**session_dict)
		print(f"VRF IP interface result is: {create_vrf_ip_interface_result}")

		print("Create VRF Network...")
		create_vrf_network_result = vrfs.create_network(
			data["segmentation_config"]["vrf_name"],
			data["segmentation_config"]["vrf_network"]["name"],
			data["segmentation_config"]["vrf_network"]["vlan_id"],
			auth_header,
			**session_dict)
		print(f"VRF Network create result is: {create_vrf_network_result}")

		print("Create Endpoint Groups...")
		create_endpoint_group_result = endpoint_group.create(
			data["segmentation_config"]["policy"]["endpoint_group"]["name"],
			data["segmentation_config"]["policy"]["endpoint_group"]["endpoints"][0]["ipv4_range"],
			auth_header,
			data["segmentation_config"]["policy"]["endpoint_group"]["type"],
			data["segmentation_config"]["policy"]["endpoint_group"]["sub_type"],
			data["segmentation_config"]["policy"]["endpoint_group"]["endpoints"][0]["type"],
			data["segmentation_config"]["policy"]["endpoint_group"]["description"],
			**session_dict)
		print(f"Endpoint group create result is: {create_endpoint_group_result}")

		print("Create policy rules...")
		for rule in data["segmentation_config"]["policy"]["rules"]:
			create_policy_rule_result = policy_rules.create(
				rule,
				auth_header,
				**session_dict)
			print(f"Create policy rule {rule['name']} result is: {create_policy_rule_result}")

		print("Create policy...")
		create_policy_result = policy.create(
			data["segmentation_config"]["policy"]["policy"],
			data["segmentation_config"]["vrf_name"],
			data["segmentation_config"]["vrf_network"]["name"],
			auth_header,
			**session_dict)
		print(f"Create policy {data['segmentation_config']['policy']['policy']['name']} result is: {create_policy_result}")
		print("Waiting for 10 seconds for vcenter data to reflect...")
		time.sleep(10)

		print("Create vswitch...")
		create_vswitch_result = vswitch.create(
			data,
			auth_header,
			**session_dict)
		print(f"Create vswitch {data['segmentation_config']['distributed_virtual_switch_name']} result is: {create_vswitch_result}")
		print("Waiting for 20 seconds...")
		time.sleep(20)
	except Exception as error:
		print('Ran into exception: {}. Logging out...'.format(error))
	session.logout(auth_header, **session_dict)


if __name__ == '__main__':
	main()