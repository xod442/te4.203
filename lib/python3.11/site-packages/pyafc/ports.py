#!/usr/bin/env python3

from requests.packages.urllib3.exceptions import InsecureRequestWarning
import urllib3
import logging

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.basicConfig(level=logging.INFO)


def get_port_by_switchname_and_portlabel(switch_name, port_label, auth_header, **kwargs):
	port_dict = get_all(auth_header, **kwargs)
	for port in port_dict:
		if port["switch_name"].casefold() == switch_name.casefold() and \
				port["port_label"].casefold() == port_label.casefold():
			return port
	return {}

def get_port_by_switch_uuid(switch_uuid, auth_header, **kwargs):
	port_dict = get_all(auth_header, **kwargs)
	for port in port_dict:
		if port["switch_uuid"].casefold() == switch_uuid.casefold():
			return port
	return {}


def get_pvlan_by_dvsname(fabric_uuid, dvs_name, auth_header, **kwargs):
	pvlan_dict = get_all_pvlans(fabric_uuid, auth_header, **kwargs)
	# print(pvlan_dict)
	for pvlan in pvlan_dict:
		if dvs_name in pvlan['name']:
			return pvlan
	return {}


def validate_vlans(expected_vlan_list, switch_name, port_label, auth_header, **kwargs):
	port_data = get_port_by_switchname_and_portlabel(
		switch_name,
		port_label,
		auth_header,
		**kwargs
	)
	actual_vlan_string = port_data['vlans']
	print(f"Actual VLAN string for, Switch - {switch_name}, Port label - {port_label}, are : {actual_vlan_string}")
	for vlan in expected_vlan_list:
		if vlan not in actual_vlan_string:
			return False
	return True


def validate_pvlans(
		fabric_uuid,
		vc_hostname,
		dvs_name,
		switch_name,
		primary_vlan,
		isolated_vlan,
		auth_header,
		**kwargs):
	pvlan_data = get_pvlan_by_dvsname(
		fabric_uuid,
		dvs_name,
		auth_header,
		**kwargs
	)
	print(f"Actual PVLAN string for, Distribute Switch - {dvs_name}, are : {pvlan_data}")
	if str(pvlan_data['primary_vlan']) in primary_vlan and pvlan_data['isolated_vlans'] in isolated_vlan:
		return True
	return False


def get_all(auth_header, **kwargs):
	target_url = kwargs["url"] + "ports?lag=true"
	# print("Target_url: " + target_url)
	response = kwargs["s"].get(target_url, headers=auth_header, verify=False)
	if response.status_code not in [200]:
		logging.warning("FAIL: get_all ports failed with status code %d: %s" % (response.status_code, response.text))
		exit(-1)
	else:
		logging.info("SUCCESS: get_all ports succeeded")
		output = response.json()
		return output['result']


def get_all_pvlans(fabric_uuid, auth_header, **kwargs):
	target_url = kwargs["url"] + f"fabrics/{fabric_uuid}/pvlans"
	# print("Target_url: " + target_url)
	response = kwargs["s"].get(target_url, headers=auth_header, verify=False)
	if response.status_code not in [200]:
		logging.warning("FAIL: get_all pvlans failed with status code %d: %s" % (response.status_code, response.text))
		exit(-1)
	else:
		logging.info("SUCCESS: get_all pvlans succeeded")
		output = response.json()
		return output['result']
