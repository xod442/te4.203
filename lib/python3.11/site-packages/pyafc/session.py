#!/usr/bin/env python3

from requests.packages.urllib3.exceptions import InsecureRequestWarning
import urllib3
import requests
import os
import sys
import logging
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.basicConfig(level=logging.INFO)


def login(base_url, username=None, password=None):
	login_headers = {
		"X-Auth-Username": username,
		"X-Auth-Password": password,
		"Content-Type": "application/json"
	}

	s = requests.Session()
	print(base_url + "auth/token")
	try:
		response = s.post(base_url + "auth/token", data=None, headers=login_headers, verify=False, timeout=5)
	except requests.exceptions.ConnectTimeout:
		logging.warning('ERROR: Error connecting to host: connection attempt timed out.')
		exit(-1)
	if response.status_code not in [200,201,204]:
		logging.warning("FAIL: Login failed with status code %d: %s" % (response.status_code, response.text))
		exit(-1)
	else:
		logging.info("SUCCESS: Login succeeded")
		output = response.json()

		auth_token = output['result']
		auth_header = {
			"Authorization": auth_token
		}

		return s, auth_header


def logout(auth_header, **kwargs):
	response = kwargs["s"].delete(kwargs["url"] + "auth/token", headers=auth_header, verify=False)

	if response.status_code not in [200]:
		logging.warning("FAIL: Logout failed with status code %d: %s" % (response.status_code, response.text))
		exit(-1)
	else:
		logging.info("SUCCESS: Logout succeeded")
		return response.json()

