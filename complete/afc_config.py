#!/usr/bin/env python3
'''
Data Center POD automatio information
2024 wookieware.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0.

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.


__author__ = "@netwookie"
__credits__ = ["Rick Kauffman"]
__license__ = "Apache2"
__version__ = "0.1.1"
__maintainer__ = "Rick Kauffman"
__email__ = "rick@rickkauffman.com"
__status__ = "Alpha"
'''

from requests.packages.urllib3.exceptions import InsecureRequestWarning

import urllib3
import time
import pyafc.session as session
import pyafc.devices as devices
import pyafc.fabric as fabric
import pyafc.leaf_spine as leaf_spine
import pyafc.vrfs as vrfs
import pyafc.ntp as ntp
import pyafc.dns as dns
import pyafc.vsx as vsx
import pyafc.underlay as underlay
import utility.pod_info as pod_info


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# Get data centrer variables
info = pod_info.pod_info()

# Build the data center
try:

	login_session, auth_header = session.login(info['base_url'], info['username'], info['password'])

	print(auth_header)
	session_dict = dict(s=login_session, url=info['base_url'])

	print("Create Fabric")
	response = fabric.create_fabric(info['fabric_name'], auth_header, info['timezone'], info['fab_description'], **session_dict)
	print("tHIS IS THE FAB_response {0}".format(response))

	print("Discovering Switches...")
	devices.discover_switches(info['switch_list'], auth_header, info['username'], info['switch_pass'], **session_dict)

	print('Waiting 60 seconds for switches to onboard to add to fabric')
	time.sleep(30)

	#print("Getting fabric UUID")
	fabric_uuid = fabric.get_fabrics_uuid(info['fabric_name'], auth_header, **session_dict)
	#print("tHIS IS THE FAB_id {0}".format(fabric_uuid))

	#print("Getting VRF UUID")
	vrf_info = vrfs.get_vrf(info['vrf_name'], auth_header, **session_dict)
	vrf_uuid = vrf_info['uuid']
	#print("tHIS IS THE VRF_info {0}".format(vrf_uuid))

	print("Adding Leaf Switches to Fabric...")
	devices.add_switches_to_fabric(info['leaf_switch_list'], auth_header, "leaf", fabric_uuid, **session_dict)

	print('Waiting 60 seconds for leaf switches to add to fabric')
	time.sleep(30)

	print("Adding Spine Switches to Fabric...")
	devices.add_switches_to_fabric(info['spine_switch_list'], auth_header, "spine", fabric_uuid, **session_dict)

	print('Waiting 60 seconds for spine switches to add to fabric')
	time.sleep(30)

	print("Adding NTP Server(s)...")
	ntp.create_ntp(info['ntp_name'], [fabric_uuid], info['ntp_ip'], auth_header, **session_dict)

	print("Adding DNS Server(s)...")
	dns.create_dns(info['dns_afc_name'], [fabric_uuid], info['domain_name'], info['name_server_list'], auth_header, **session_dict)

	print('Creating the VSX pairs')
	vsx.create_vsxes(fabric_uuid, auth_header, **session_dict)

	print('Creating the leaf-spine')
	leaf_spine.create_leaf_spine(fabric_uuid, auth_header, **session_dict)

	print('Creating the underlay network - OSPF')
	underlay.create_underlay(vrf_uuid, auth_header,**session_dict)



except Exception as error:
	print('Ran into exception: {}. Logging out...'.format(error))


	session.logout(auth_header, **session_dict)
