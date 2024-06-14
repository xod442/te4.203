#!/usr/bin/env python3

from requests.packages.urllib3.exceptions import InsecureRequestWarning
import pyafc.policy_rules as policy_rules
import pyafc.vrfs as vrfs
import urllib3
import logging

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.basicConfig(level=logging.INFO)


def get_policy(policy_name, auth_header, **kwargs):
	uuid = get_uuid(policy_name, auth_header, **kwargs)
	target_url = kwargs["url"] + "policies/{}".format(uuid)
	response = kwargs["s"].get(target_url, headers=auth_header, verify=False)
	if response.status_code not in [200]:
		logging.warning("FAIL: get_policy failed with status code %d: %s" % (response.status_code, response.text))
		exit(-1)
	else:
		logging.info("SUCCESS: get_policy succeeded")
		output = response.json()
		return output['result']


def enable_rule(policy_name, rule_name, auth_header, **kwargs):
	rule_uuid = policy_rules.get_uuid(rule_name, auth_header, **kwargs)
	policy_data = get_policy(policy_name, auth_header, **kwargs)
	rules_disabled = policy_data['rules_disabled']
	new_rules_disabled = []
	for rule_id in rules_disabled:
		if rule_uuid != rule_id:
			new_rules_disabled.append(rule_id)
	policy_data['rules_disabled'] = new_rules_disabled
	return update_policy(policy_data, auth_header, **kwargs)


def disable_rule(policy_name, rule_name, auth_header, **kwargs):
	rule_uuid = policy_rules.get_uuid(rule_name, auth_header, **kwargs)
	policy_data = get_policy(policy_name, auth_header, **kwargs)
	rules_disabled = policy_data['rules_disabled']
	rules_disabled.append(rule_uuid)
	policy_data['rules_disabled'] = rules_disabled
	return update_policy(policy_data, auth_header, **kwargs)


def update_policy(data, auth_header, **kwargs):
	# Update policy
	target_url = kwargs["url"] + f"policies/{data['uuid']}"
	response = kwargs["s"].put(target_url, json=data, headers=auth_header, verify=False)
	if response.status_code not in [200]:
		logging.warning("FAIL: update policy failed with status code %d: %s" % (response.status_code, response.text))
		exit(-1)
	else:
		logging.info("SUCCESS: update policy succeeded")
		output = response.json()
		return output
	# print(data)


def create(data, vrf_name, vrf_network_name, auth_header, **kwargs):

	uuid = get_uuid(data['name'], auth_header, **kwargs)
	if uuid:
		print(f"Rule: {data['name']}, Already exist. Skipping...")
		return {}

	target_url = kwargs["url"] + "policies"
	data["rules"] = policy_rules.convert_name_list_to_uuid_list(data["rules"],auth_header,**kwargs)
	data["enforcers"][0]["uuid"] = vrfs.get_network_uuid(vrf_name, vrf_network_name, auth_header,**kwargs)
	response = kwargs["s"].post(target_url, json=data, headers=auth_header, verify=False)
	if response.status_code not in [200]:
		logging.warning("FAIL: create policy failed with status code %d: %s" % (response.status_code, response.text))
		exit(-1)
	else:
		logging.info("SUCCESS: create policy succeeded")
		output = response.json()
		return output


def delete(name, auth_header, **kwargs):
	uuid = get_uuid(name, auth_header, **kwargs)
	if not uuid:
		return {}
	target_url = kwargs["url"] + "policies/{}".format(uuid)

	response = kwargs["s"].delete(target_url, headers=auth_header, verify=False)
	if response.status_code not in [200]:
		logging.warning("FAIL: delete policies failed with status code %d: %s" % (response.status_code, response.text))
		exit(-1)
	else:
		logging.info("SUCCESS: delete policies succeeded")
		output = response.json()
		return output


def get_uuid(name, auth_header, **kwargs):
	policies_dict = get_all(auth_header, **kwargs)
	uuid = ""
	for policy in policies_dict:
		if policy["name"].casefold() == name.casefold():
			uuid = policy["uuid"]
	return uuid


def get_all(auth_header, **kwargs):
	target_url = kwargs["url"] + "policies"
	response = kwargs["s"].get(target_url, headers=auth_header, verify=False)
	if response.status_code not in [200]:
		logging.warning("FAIL: get_all policies failed with status code %d: %s" % (response.status_code, response.text))
		exit(-1)
	else:
		logging.info("SUCCESS: get_all policies succeeded")
		output = response.json()
		return output['result']