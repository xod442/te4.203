#!/usr/bin/env python3

from requests.packages.urllib3.exceptions import InsecureRequestWarning

import urllib3
import requests
import os
import sys
import logging
import json
import pyafc.session as session
import pyafc.devices as devices
import pyafc.fabric as fabric
import pyafc.leaf_spine as leaf_spine
import pyafc.vrfs as vrfs
import pyafc.ntp as ntp
import pyafc.dns as dns
import pyafc.vsx as vsx
import pyafc.underlay as underlay

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.basicConfig(level=logging.INFO)

def build():


	try:
		login_session, auth_header = session.login(base_url, username, password)

		print(auth_header)
		session_dict = dict(s=login_session, url=base_url)

		print("Create Fabric")
		response = fabric.create_fabric(fabric_name, auth_header, timezone, description, **session_dict)
		print("tHIS IS THE FAB_response {0}".format(response))

		print("Discovering Switches...")
		devices.discover_switches(switch_list, auth_header, switch_pass, password, **session_dict)


		#print("Getting fabric UUID")
		fabric_uuid = fabric.get_fabrics_uuid(fabric_name, auth_header, **session_dict)
		#print("tHIS IS THE FAB_id {0}".format(fabric_uuid))

		#print("Getting VRF UUID")
		vrf_info = vrfs.get_vrf(vrf_name, auth_header, **session_dict)
		vrf_uuid = vrf_info['uuid']
		#print("tHIS IS THE VRF_info {0}".format(vrf_uuid))


		print("Adding Leaf Switches to Fabric...")
		devices.add_switches_to_fabric(leaf_switch_list, auth_header, "leaf", fabric_uuid, **session_dict)

		print("Adding Spine Switches to Fabric...")
		devices.add_switches_to_fabric(spine_switch_list, auth_header, "spine", fabric_uuid, **session_dict)

		print("Adding NTP Server(s)...")
		ntp.create_ntp(ntp_name, [fabric_uuid], ntp_ip, auth_header, **session_dict)

		print("Adding DNS Server(s)...")
		dns.create_dns(dns_afc_name, [fabric_uuid], domain_name, name_server_list, auth_header, **session_dict)



		print('Creating the VSX pairs')
		vsx.create_vsxes(fabric_uuid, auth_header, **session_dict)

		print('Creating the leaf-spine')
		leaf_spine.create_leaf_spine(fabric_uuid, auth_header, **session_dict)


		print('Creating the underlay network - OSPF')
		underlay.create_underlay(vrf_uuid, auth_header,**session_dict)



	except Exception as error:
		print('Ran into exception: {}. Logging out...'.format(error))
	session.logout(auth_header, **session_dict)


if __name__ == '__main__':

	#
	# Setup psystem Parameters - Dont put passwors in you code!
	# It's ok for testing purposes but watch out when saving to github
	#
	afc_ip = "10.251.1.30"
	username = "admin"
	password = "admin"
	switch_pass = "admin"
	auth_header = {}

	os.environ['no_proxy'] = afc_ip
	os.environ['NO_PROXY'] = afc_ip

	base_url = "https://{0}/api/v1/".format(afc_ip)

	leaf_switch_list = [
		"10.251.1.12",
		"10.251.1.13",
		"10.251.1.14",
		"10.251.1.15"
	]

	spine_switch_list = [
		"10.251.1.11"
	]


	# OSPF Underlay Section
	underlay_type = "OSPF"
	name = "Pod 1_underlay"
	description = "My_Underlay"
	ipv4_address = "10.100.10.0"
	ipv4_prefix_length = 24
	transit_vlan = 4000


	switch_list = leaf_switch_list + spine_switch_list

	fabric_name = "dsa"
	description = "This fabric is pod 1"
	timezone="America/Los_Angeles"
	vrf_name = "default"
	ntp_name = "ntp-fabric"
	ntp_ip = "10.251.1.1"
	dns_afc_name = "dns-fabric"
	domain_name = "lab.local"
	name_server_list = ["10.251.1.1"]

	#now call build from above
	build()
