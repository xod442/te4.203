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
import pyafc.devices as devices
import pyafc.fabric as fabric
import pyafc.vrfs as vrfs
import pyafc.ntp as ntp
import pyafc.dns as dns
import time
import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.basicConfig(level=logging.INFO)

def main():
	# Take input from JSON file
	data = json.loads(open(sys.argv[1], "r").read())  # Combined input
	print(datetime.datetime.now())

	fabric_name = data['fabric_name']
	vrf_name = data['vrf_ip_interface_config']['vrf_name']
	ntp_name = data['ntp_name']
	ntp_ip = data['ntp_ip']
	dns_afc_name = data['dns_afc_name']
	domain_name = data['domain_name']
	name_server_list = data['name_server_list']
	afc_ip = data['afc_ip']
	username = data['username']
	password = data['password']
	switch_pass = data['switch_pass']
	leaf_switch_list = data['leaf_switch_list']
	spine_switch_list = data['spine_switch_list']

	auth_header = {}
	os.environ['no_proxy'] = afc_ip
	os.environ['NO_PROXY'] = afc_ip
	base_url = "https://{0}/api/v1/".format(afc_ip)

	switch_list = leaf_switch_list + spine_switch_list

	try:
		login_session, auth_header = session.login(base_url, username, password)

		#print(auth_header)
		session_dict = dict(s=login_session, url=base_url)

		print("Create Fabric")
		fabric.create_fabric(fabric_name, auth_header, **session_dict)

		print("Getting fabric UUID")
		fabric_uuid = fabric.get_fabrics_uuid(fabric_name, auth_header, **session_dict)

		print("Discovering Switches...")
		devices.discover_switches(switch_list, auth_header, switch_pass, password, **session_dict)

		print("Adding Leaf Switches to Fabric...")
		devices.add_switches_to_fabric(leaf_switch_list, auth_header, "leaf", fabric_uuid, **session_dict)

		print("Adding Spine Switches to Fabric...")
		devices.add_switches_to_fabric(spine_switch_list, auth_header, "spine", fabric_uuid, **session_dict)

		print("Adding NTP Server(s)...")
		ntp.create_ntp(ntp_name, [fabric_uuid], ntp_ip, auth_header, **session_dict)

		print("Adding DNS Server(s)...")
		dns.create_dns(dns_afc_name, [fabric_uuid], domain_name, name_server_list, auth_header, **session_dict)

		time.sleep(10)
		print("Creating VRF")
		vrfs.create_vrf(vrf_name, fabric_uuid, auth_header, primary_route_target="65001:101",
						address_family="ipv4_unicast", route_mode="both", max_routes=0, vni=5, **session_dict)

	except Exception as error:
		print('Ran into exception: {}. Logging out...'.format(error))
	session.logout(auth_header, **session_dict)


if __name__ == '__main__':
	main()