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
import pyafc.vrfs as vrfs
import pyafc.vsx as vsx
import pyafc.leaf_spine as leaf_spine
import pyafc.underlay as underlay
import pyafc.overlay as overlay
import pyafc.evpn as evpn
import datetime
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.basicConfig(level=logging.INFO)

def main():
	# Take input from JSON file
	data = json.loads(open(sys.argv[1], "r").read())  # Combined input
	print(datetime.datetime.now())

	fabric_name = data['fabric_name']
	vrf_name = data['vrf_ip_interface_config']['vrf_name']
	afc_ip = data['afc_ip']
	username = data['username']
	password = data['password']
	switch_pass = data['switch_pass']
	leaf_switch_list = data['leaf_switch_list']
	spine_switch_list = data['spine_switch_list']
	vrf_default_name = data['underlay_config']['vrf_default_name']
	# automatic_evpn_list = data['automatic_evpn_list']
	new_leaf_switch_list = data['new_leaf_switch_list']

	auth_header = {}
	os.environ['no_proxy'] = afc_ip
	os.environ['NO_PROXY'] = afc_ip
	base_url = "https://{0}/api/v1/".format(afc_ip)
	leaf_switch_list = new_leaf_switch_list + leaf_switch_list
	switch_list = leaf_switch_list + spine_switch_list

	try:
		login_session, auth_header = session.login(base_url, username, password)

		#print(auth_header)
		session_dict = dict(s=login_session, url=base_url)

		print("Getting fabric UUID")
		fabric_uuid = fabric.get_fabrics_uuid(fabric_name, auth_header, **session_dict)
		print(f"Fabric UUID: {fabric_uuid}")

		print("Discovering Switches...")
		devices.discover_switches(switch_list, auth_header, switch_pass, password, **session_dict)

		print("Adding Leaf Switches to Fabric...")
		devices.add_switches_to_fabric(new_leaf_switch_list, auth_header, "leaf", fabric_uuid, **session_dict)

		time.sleep(60) # Wait for VSX pair to appear. Will use netter way for pair to be available
		# print("Cleaning up All VSX Pairs...")
		# vsx.delete_all_vsx_pairs(fabric_name, auth_header, **session_dict)
		# time.sleep(60) # Wait for VSX pair to appear. Will use netter way for pair to be available

		print("Create VSX...")
		vsx_ids = vsx.create_vsxes(fabric_uuid, auth_header, **session_dict)
		print(vsx_ids)

		# TODO: Delete VSX Pair for spine "myVSXPair_Zone1-Rack1-Spine1_Zone1-Rack1-Spine2"
		print("Create Leaf Spine...")
		leaf_spine_ids = leaf_spine.create_leaf_spine(
			fabric_uuid,
			auth_header,
			name_prefix=data['leaf_spine_config']['name_prefix'],
			description=data['leaf_spine_config']['description'],
			**session_dict)
		print(leaf_spine_ids)

		print("Getting VRF UUID")
		vrf_uuid = vrfs.get_vrfs_uuid(vrf_default_name, auth_header, **session_dict)
		print(f"VRF UUID: {vrf_uuid}")

		print("Create Underlay...")
		underlay_ids = underlay.create_underlay(
			vrf_uuid,
			auth_header,
			underlay_type=data["underlay_config"]['underlay_type'],
			name=data["underlay_config"]['name'],
			description=data["underlay_config"]['description'],
			ipv4_address=data["underlay_config"]['ipv4_address'],
			ipv4_prefix_length=data["underlay_config"]['ipv4_prefix_length'],
			transit_vlan=data["underlay_config"]['transit_vlan'],
			**session_dict)
		print(f"Underlay Ids: {underlay_ids}")

		print("Getting VRF UUID")
		vrf_uuid = vrfs.get_vrfs_uuid(vrf_default_name, auth_header, **session_dict)
		print(f"VRF UUID: {vrf_uuid}")

		spine_switch_dict = devices.get_switches_uuids(spine_switch_list, auth_header, **session_dict)
		spine_switch_list = []
		for spine_switch in spine_switch_dict:
			spine_switch_list.append(spine_switch_dict[spine_switch])
		print(f"Spine switch list: {spine_switch_list}")
		print("Create Overlay...")
		underlay_ids = overlay.create_overlay(
			vrf_uuid,
			auth_header,
			bgp_type=data["ovrerlay_config"]['bgp_type'],
			name=data["ovrerlay_config"]['name'],
			description=data["ovrerlay_config"]['description'],
			spine_ids=spine_switch_list,
			spine_leaf_asn=data["ovrerlay_config"]['spine_leaf_asn'],
			ipv4_address=data["ovrerlay_config"]['ipv4_address'],
			ipv4_prefix_length=data["ovrerlay_config"]['ipv4_prefix_length'],
			**session_dict)
		print(f"Overlay Ids: {underlay_ids}")

		# print("Delete automatic EVPN...")
		# # TODO: Delete only if it exist
		# for evpn_name in automatic_evpn_list:
		# 	evpn.delete_evpn(evpn_name, auth_header, **session_dict)

		print("Get UUIDs of leaf switches...")
		leaf_switch_dict = devices.get_switches_uuids(leaf_switch_list, auth_header, **session_dict)
		leaf_switch_uuid_list = []
		for leaf_switch in leaf_switch_dict:
			leaf_switch_uuid_list.append(leaf_switch_dict[leaf_switch])
		print(f"Leaf switch list: {leaf_switch_uuid_list}")
		evpn_result = evpn.create_evpn(
			data["evpn_config"]["evpn_prefix"],
			fabric_uuid,
			auth_header,
			switch_uuids=leaf_switch_uuid_list,
			mac_range_lower=data["evpn_config"]["mac_range_lower"],
			mac_range_upper=data["evpn_config"]["mac_range_upper"],
			vlans=data["evpn_config"]["vlans"],
			description=data["evpn_config"]["description"],
			rt_type=data["evpn_config"]["rt_type"],
			administrative_num=data["evpn_config"]["administrative_num"],
			vni=data["evpn_config"]["vni"],
			**session_dict)
		print(f"EVPN status per switch: {evpn_result}")

		print("Create VRF IP Interfaces...")
		leaf_switch_dict = devices.get_switches_uuids(leaf_switch_list, auth_header, **session_dict)
		leaf_switch_uuid_list = []
		for leaf_switch in leaf_switch_dict:
			leaf_switch_uuid_list.append(leaf_switch_dict[leaf_switch])
		print(f"Leaf switch list: {leaf_switch_uuid_list}")

		create_vrf_ip_interface_result = vrfs.create_ip_interfaces(
			data["vrf_ip_interface_config"]["vrf_name"],
			leaf_switch_uuid_list[0],
			auth_header,
			name=data["vrf_ip_interface_config"]["name"],
			active_gateway_ipv4_address=data["vrf_ip_interface_config"]["active_gateway_ipv4_address"],
			active_gateway_mac_address=data["vrf_ip_interface_config"]["active_gateway_mac_address"],
			ipv4_primary_addres_address=data["vrf_ip_interface_config"]["ipv4_primary_addres_address"],
			ipv4_primary_address_prefix_length=data["vrf_ip_interface_config"]["ipv4_primary_address_prefix_length"],
			if_type=data["vrf_ip_interface_config"]["if_type"],
			description = data["vrf_ip_interface_config"]["description"],
			vlan = data["vrf_ip_interface_config"]["vlan"],
			ipv4_secondary_address = data["vrf_ip_interface_config"]["ipv4_secondary_address"],
			**session_dict)
		print(f"VRF IP interface create result is: {create_vrf_ip_interface_result}")

	except Exception as error:
		print('Ran into exception: {}. Logging out...'.format(error))
	session.logout(auth_header, **session_dict)


if __name__ == '__main__':
	main()