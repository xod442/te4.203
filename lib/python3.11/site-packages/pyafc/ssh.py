#!/usr/bin/env python3

from requests.packages.urllib3.exceptions import InsecureRequestWarning
import logging
import paramiko

# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.basicConfig(level=logging.INFO)


def connect(host, username, password):
	client = paramiko.client.SSHClient()
	client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	client.connect(host, username=username, password=password)
	return client


def is_ping_ok(
		host,
		username,
		password,
		ping_ip="10.20.30.40",timeout_seconds=5):

	client = connect(host, username, password)
	_stdin, _stdout, _stderr = client.exec_command(f"ping -w {timeout_seconds} {ping_ip}")
	output = _stdout.read().decode()
	print(output)
	client.close()
	if "100% packet loss" in output:
		return False
	return True
