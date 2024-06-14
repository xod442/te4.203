#!/usr/bin/env python3
'''
Data Center POD automation information
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
__status__ = "Alpha"
'''

import urllib3
from requests.packages.urllib3.exceptions import InsecureRequestWarning

import pyafc.session as session
import pyafc.devices as devices
import pyafc.fabric as fabric
import pyafc.leaf_spine as leaf_spine
import pyafc.vrfs as vrfs
import pyafc.ntp as ntp
import pyafc.dns as dns
import pyafc.vsx as vsx
import pyafc.ports as ports
import pyafc.underlay as underlay
import pod_info as pod_info



urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# Get data centrer variables
info = pod_info.pod_info()

try:
    print('Example')
    '''
    ====================================================================
    |                                                                  |
    |          BLOCK OF CODE GOES HERE BETWEEN TRY AND EXCEPT          |
    |                                                                  |
    ====================================================================

    '''

except Exception as error:
    print('Ran into exception: {}. Logging out...'.format(error))


    session.logout()
