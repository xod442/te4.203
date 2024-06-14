#!/usr/bin/env python3
# coding=utf-8
# author: @netwookie.
# -*- coding: utf-8 -*-
'''
                     _ _
  _ __ _  _ _ __  ___| | |___ _ _
 | '_ \ || | '  \/ -_) | / _ \ ' \
 | .__/\_, |_|_|_\___|_|_\___/_||_|
 |_|   |__/

A python binind for Mellanox ONX ethernet switches

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#  http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# __author__ = "@netwookie"
# __credits__ = ["Rick Kauffman"]
# __license__ = "Apache2.0"
# __maintainer__ = "Rick Kauffman"
# __email__ = "rick@rickkauffman.com"

'''
import urllib3
urllib3.disable_warnings()
from pymellon.auth import Auth
import json
import requests

class Management(Auth):

    def __init__(
            self, host,
            username, password
            ):

        Auth.__init__(self, host, username, password)

        self.headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'cookie': self.key
        }

        self.params = {
            'script': 'json',
        }

        self.endpoint ='http://' + host +  '/admin/launch'


    def get_running_config(self):

        self.data = {"cmd": "show running"}
        self.data= json.dumps(self.data)
        response = requests.post(self.endpoint,params=self.params,headers=self.headers,data=self.data)

        return response.text
