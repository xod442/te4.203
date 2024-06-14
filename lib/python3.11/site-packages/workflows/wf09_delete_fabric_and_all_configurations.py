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
import pyafc.vsx as vsx
import pyafc.leaf_spine as leaf_spine
import pyafc.evpn as evpn

import pyafc.ntp as ntp
import pyafc.dns as dns
import datetime
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.basicConfig(level=logging.INFO)

FAILCHECK

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
	new_leaf_switch_list = data['new_leaf_switch_list']
	# automatic_evpn_list = data['automatic_evpn_list']

	auth_header = {}
	os.environ['no_proxy'] = afc_ip
	os.environ['NO_PROXY'] = afc_ip
	base_url = "https://{0}/api/v1/".format(afc_ip)

	switch_list = leaf_switch_list + spine_switch_list + new_leaf_switch_list

	try:
		login_session, auth_header = session.login(base_url, username, password)

		# print(auth_header)
		session_dict = dict(s=login_session, url=base_url)

		print("Getting Switch UUIDs...")
		print(devices.get_switches_uuids(switch_list, auth_header, **session_dict))

		print("Deleting All VSX Pairs...")
		vsx.delete_all_vsx_pairs(fabric_name, auth_header, **session_dict)
		time.sleep(5)

		print("Deleting All Leaf Spine...")
		leaf_spine.delete_all(auth_header, **session_dict)

		print("Delete All EVPNs")
		fabric_uuid = fabric.get_fabrics_uuid(fabric_name, auth_header, **session_dict)
		evpns = evpn.get_all_evpn(auth_header, **session_dict)
		for evpn_obj in evpns:
			print(evpn_obj['name'])
			if fabric_uuid in evpn_obj['fabric_uuid']:
				evpn.delete_evpn(evpn_obj['name'], auth_header, **session_dict)

		print("Deleting Switches...")
		devices.delete_switches_from_afc(switch_list, auth_header, **session_dict)

		print("Deleting NTP configuration for NTP server named {}".format(ntp_name))
		ntp.delete_ntp(ntp_name, auth_header, **session_dict)

		print("Deleting DNS configuration for DNS server named {}".format(dns_afc_name))
		dns.delete_dns(dns_afc_name, auth_header, **session_dict)

		print("Deleting All IP interfaces for VRF named {}".format(fabric_name))
		vrfs.delete_all_ip_interfaces(vrf_name, auth_header, **session_dict)
		print("Deleting VRF named {}".format(fabric_name))
		vrfs.delete_vrf(vrf_name, auth_header, **session_dict)

		print("Deleting Fabric named {}".format(fabric_name))
		fabric.delete_fabric(fabric_name, auth_header, **session_dict)


	except Exception as error:
		print('Ran into exception: {}. Logging out...'.format(error))
	session.logout(auth_header, **session_dict)


if __name__ == '__main__':
	main()