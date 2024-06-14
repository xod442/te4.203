#!/usr/bin/env python3

from requests.packages.urllib3.exceptions import InsecureRequestWarning
import urllib3
import logging

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.basicConfig(level=logging.INFO)


def get_all_vrfs(auth_header, **kwargs):
	target_url = kwargs["url"] + "vrfs"
	response = kwargs["s"].get(target_url, headers=auth_header, verify=False)
	if response.status_code not in [200]:
		logging.warning("FAIL: get_all_vrfs failed with status code %d: %s" % (response.status_code, response.text))
		exit(-1)
	else:
		logging.info("SUCCESS: get_all_vrfs succeeded")
		output = response.json()
		return output['result']


def get_all_vrf_ipinterfaces(vrf_name, auth_header, **kwargs):
	uuid = get_vrfs_uuid(vrf_name, auth_header, **kwargs)
	target_url = kwargs["url"] + f"vrfs/{uuid}/ip_interfaces"
	response = kwargs["s"].get(target_url, headers=auth_header, verify=False)
	if response.status_code not in [200]:
		logging.warning("FAIL: get_all_vrf_ipinterfaces failed with status code %d: %s" % (response.status_code, response.text))
		exit(-1)
	else:
		logging.info("SUCCESS: get_all_vrf_ipinterfaces succeeded")
		output = response.json()
		return output['result']


def get_all_vrf_network(vrf_name, auth_header, **kwargs):
	uuid = get_vrfs_uuid(vrf_name, auth_header, **kwargs)
	target_url = kwargs["url"] + f"vrfs/{uuid}/networks"
	response = kwargs["s"].get(target_url, headers=auth_header, verify=False)
	if response.status_code not in [200]:
		logging.warning("FAIL: get_all_vrf_network failed with status code %d: %s" % (response.status_code, response.text))
		exit(-1)
	else:
		logging.info("SUCCESS: get_all_vrf_network succeeded")
		output = response.json()
		return output['result']


def get_all_networks(vrf_name, auth_header, **kwargs):
	uuid = get_vrfs_uuid(vrf_name, auth_header, **kwargs)
	target_url = kwargs["url"] + f"vrfs/{uuid}/networks"
	response = kwargs["s"].get(target_url, headers=auth_header, verify=False)
	if response.status_code not in [200]:
		logging.warning("FAIL: get_all_networks failed with status code %d: %s" % (response.status_code, response.text))
		exit(-1)
	else:
		logging.info("SUCCESS: get_all_networks succeeded")
		output = response.json()
		return output['result']


def get_vrf(vrf_name, auth_header, **kwargs):
	uuid = get_vrfs_uuid(vrf_name, auth_header, **kwargs)
	target_url = kwargs["url"] + "vrfs/{}".format(uuid)
	response = kwargs["s"].get(target_url, headers=auth_header, verify=False)
	if response.status_code not in [200]:
		logging.warning("FAIL: get_vrf failed with status code %d: %s" % (response.status_code, response.text))
		exit(-1)
	else:
		logging.info("SUCCESS: get_vrf succeeded")
		output = response.json()
		return output['result']


def delete_all_ip_interfaces(vrf_name, auth_header, **kwargs):
	uuid = get_vrfs_uuid(vrf_name, auth_header, **kwargs)
	target_url = kwargs["url"] + f"vrfs/{uuid}/ip_interfaces"
	response = kwargs["s"].delete(target_url, headers=auth_header, verify=False)
	if response.status_code not in [200]:
		logging.warning("FAIL: delete_all_ip_interfaces failed with status code %d: %s" % (response.status_code, response.text))
		exit(-1)
	else:
		logging.info("SUCCESS: delete_all_ip_interfaces succeeded")
		output = response.json()
		return output


def get_network_uuid(vrf_name, network_name, auth_header, **kwargs):
	network_dict = get_all_networks(vrf_name, auth_header, **kwargs)
	uuid = ""
	for network in network_dict:
		if network["name"].casefold() == network_name.casefold():
			uuid = network["uuid"]
	return uuid


def create_network(
		vrf_name,
		network_name,
		vlan_id,
		auth_header,
		description="",
		max_cps_mode="unlimited",
		max_sessions_mode="unlimited",
		**kwargs):

	uuid = get_vrf_network_uuid(vrf_name, network_name, auth_header, **kwargs)
	if uuid:
		print(f"VRF network {network_name}, is already added on VRF {vrf_name}, skipping...")
		return {}
	vrf_uuid = get_vrfs_uuid(vrf_name, auth_header, **kwargs)
	print(f"VRF UUID: {vrf_uuid}")
	target_url = kwargs["url"] + f"vrfs/{vrf_uuid}/networks"

	data = {
		"name":network_name,
   		"description":description,
   		"vlan_id":int(vlan_id),
   		"max_cps_mode":max_cps_mode,
   		"max_sessions_mode":max_sessions_mode
	}
	response = kwargs["s"].post(target_url, json=data, headers=auth_header, verify=False)
	if response.status_code not in [200]:
		logging.warning("FAIL: create_network creation failed with status code %d: %s" % (response.status_code, response.text))
		exit(-1)
	else:
		logging.info("SUCCESS: create_network succeeded")
		output = response.json()
		return output["result"]


def create_ip_interfaces(
		vrf_name,
		switch_uuid,
		lag_uuid,
		auth_header,
		name="myVrfIPInterface",
		active_gateway_ipv4_address="192.168.1.10",
		active_gateway_mac_address="00:00:00:00:00:01",
		ipv4_primary_addres_address="192.168.1.100",
		ipv4_primary_address_prefix_length=24,
		if_type = "vlan",
		description = "",
	    vlan = 1,
		ipv4_secondary_address = [],
		**kwargs):

	vrf_ip_interface_uuid = get_vrf_ipinterface_uuid(vrf_name, name, auth_header, **kwargs)
	if vrf_ip_interface_uuid:
		print(f"VRF ip interface {name}, is already added on VRF {vrf_name}, skipping...")
		return {}
	vrf_uuid = get_vrfs_uuid(vrf_name, auth_header, **kwargs)
	print(f"VRF UUID: {vrf_uuid}")
	target_url = kwargs["url"] + f"vrfs/{vrf_uuid}/ip_interfaces"
	data = [
		{
			"enable": True,
			"if_type": if_type,
			"description": description,
			"switch_uuid": switch_uuid,
			"lag_uuid": lag_uuid,
			"vlan": vlan,
			"vsx_shutdown_on_split": False,
			"active_gateway": {
				"ipv4_address": active_gateway_ipv4_address,
				"mac_address": active_gateway_mac_address
			},
			"ipv4_primary_address": {
				"address": ipv4_primary_addres_address,
				"prefix_length": ipv4_primary_address_prefix_length
			},
			"name": name,
			"local_proxy_arp_enabled": True,
			"ipv4_secondary_addresses": ipv4_secondary_address
		}
	]

	response = kwargs["s"].post(target_url, json=data, headers=auth_header, verify=False)
	if response.status_code not in [200]:
		logging.warning("FAIL: create_ip_interfaces creation failed with status code %d: %s" % (response.status_code, response.text))
		exit(-1)
	else:
		logging.info("SUCCESS: create_ip_interfaces succeeded")
		output = response.json()
		return output["result"]


def create_vrf(
		vrf_name,
		fabric_uuid,
		auth_header,
		switch_uuids=[],
		primary_route_target="65001:101",
		address_family="ipv4_unicast",
		evpn=False, route_mode="both",
		description="",
		route_distinguisher="",
		secondary_route_target=[],
		max_routes=0,
		vni=1,
		**kwargs):

	target_url = kwargs["url"] + "vrfs"
	uuid = get_vrfs_uuid(vrf_name, auth_header, **kwargs)
	if uuid:
		print(f"VRF {vrf_name}, is already added, skipping...")
		return {}

	data = {
		"fabric_uuid": fabric_uuid,
		"switch_uuids": switch_uuids,
		"name": vrf_name,
		"description": description,
		"route_target": {
			"primary_route_target": {
				"as_number": primary_route_target,
				"address_family": address_family,
				"evpn": evpn,
				"route_mode": route_mode
			},
			"secondary_route_targets": secondary_route_target
		},
		"route_distinguisher": route_distinguisher,
		"max_routes": max_routes,
		"vni": vni
	}

	response = kwargs["s"].post(target_url, json=data, headers=auth_header, verify=False)
	if response.status_code not in [200]:
		logging.warning("FAIL: create_vrf failed with status code %d: %s" % (response.status_code, response.text))
		exit(-1)
	else:
		logging.info("SUCCESS: create_vrf succeeded")
		output = response.json()
		return output


def delete_vrf(vrf_name, auth_header, **kwargs):
	uuid = get_vrfs_uuid(vrf_name, auth_header, **kwargs)
	if uuid:
		target_url = kwargs["url"] + "vrfs/{}".format(uuid)
		response = kwargs["s"].delete(target_url, headers=auth_header, verify=False)
		if response.status_code not in [200]:
			logging.warning("FAIL: delete_vrf failed with status code %d: %s" % (response.status_code, response.text))
			exit(-1)
		else:
			logging.info("SUCCESS: delete_vrf succeeded")
			output = response.json()
			return output


def get_vrfs_uuid(vrf_name, auth_header, **kwargs):
	vrf_dict = get_all_vrfs(auth_header, **kwargs)
	uuid = ""
	for vrf in vrf_dict:
		if vrf["name"].casefold() == vrf_name.casefold():
			uuid = vrf["uuid"]
	return uuid


def get_vrf_ipinterface_uuid(vrf_name, ipinterface_name, auth_header, **kwargs):
	ip_interface_dict = get_all_vrf_ipinterfaces(vrf_name, auth_header, **kwargs)
	for ip_interface in ip_interface_dict:
		if ip_interface["name"].casefold() == ipinterface_name.casefold():
			return ip_interface["uuid"]
	return ""


def get_vrf_network_uuid(vrf_name, network_name, auth_header, **kwargs):
	network_dict = get_all_vrf_network(vrf_name, auth_header, **kwargs)
	for network in network_dict:
		if network["name"].casefold() == network_name.casefold():
			return network["uuid"]
	return ""


def get_vrf_by_fabric_uuid(fabric_uuid, vrf_name, auth_header, **kwargs):
	vrf_dict = get_all_vrfs(auth_header, **kwargs)
	uuid = ""
	for vrf in vrf_dict:
		if vrf["fabric_uuid"].casefold() == fabric_uuid.casefold and vrf["name"].casefold == vrf_name.casefold():
			uuid = vrf["uuid"]
	return uuid


def create_layer3_ip_interfaces(
		vrf_uuid,
		switch_uuid,
		lag_uuid,
		auth_header,
		name="myVrfIPInterface",
		ipv4_primary_addres_address="192.168.1.100",
		ipv4_primary_address_prefix_length=24,
		if_type = "routed",
		description = "",
		ipv4_secondary_address = [],
		**kwargs):

	target_url = kwargs["url"] + f"vrfs/{vrf_uuid}/ip_interfaces"
	data = [
		{
			"enable": True,
			"if_type": if_type,
			"description": description,
			"switch_uuid": switch_uuid,
			"lag_uuid": lag_uuid,
			"ipv4_primary_address": {
				"address": ipv4_primary_addres_address,
				"prefix_length": ipv4_primary_address_prefix_length
			},
			"name": name,
			"local_proxy_arp_enabled": True,
			"ipv4_secondary_addresses": ipv4_secondary_address
		}
	]



	response = kwargs["s"].post(target_url, json=data, headers=auth_header, verify=False)
	if response.status_code not in [200]:
		logging.warning("FAIL: create_ip_interfaces creation failed with status code %d: %s" % (response.status_code, response.text))
		exit(-1)
	else:
		logging.info("SUCCESS: create_ip_layer3_interfaces succeeded")
		output = response.json()
		return output["result"]
