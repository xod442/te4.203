'''
Data Center POD automation script
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

def pod_info():
    afc_ip = '10.251.1.30'

    leaf_switch_list = ["10.251.1.12",
                        "10.251.1.13",
                        "10.251.1.14",
                        "10.251.1.15"
                    ]
    spine_switch_list = ["10.251.1.11"]

    switch_list = leaf_switch_list + spine_switch_list

    base_url = "https://{0}/api/v1/".format(afc_ip)

    name_server_list = ['10.251.1.1']

    pod_info = {
                'afc_ip':afc_ip,
                'username' :'admin',
                'password' : 'admin',
                'switch_pass': 'admin',
                'auth_header' : {},
                'switch_list': switch_list,
                'leaf_switch_list' : leaf_switch_list,
                'spine_switch_list' : spine_switch_list,
                'base_url' : base_url,
                'underlay_type' : 'OSPF',
                'name' : 'Pod 1_underlay',
                'description' : 'My_Underlay',
                'ipv4_address' : '10.100.10.0',
                'ipv4_prefix_length' : 24,
                'transit_vlan' : 4000,
                'fabric_name' : 'dsa',
                'fab_description' : 'This fabric is pod 1',
                'timezone' : 'America/Los_Angeles',
                'vrf_name' : 'default',
                'ntp_name' : 'ntp-fabric',
                'ntp_ip' : '10.251.1.1',
                'name_prefix' : 'MySL',
                'slDescription' : 'MySL',
                'dns_afc_name' : 'dns-fabric',
                'domain_name' : 'lab.local',
                'name_server_list' : name_server_list
                }
    return pod_info
