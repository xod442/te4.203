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



try:
    # A simple print statement
    x = 'Hello World!'
    print(x)

    # A complex print statement 
    print(f"This is the thing every dumb intro script prints.... {x}")
    
    # A python list [] is just a list of things
    my_list = ['one','two','three','four']
    print(my_list)
    
    # Numbers in lists
    my_list = [4,100,3,44.8]
    print(my_list)
    
    # Mixed lists 
    my_list = ['hello',2644,'world',9999999]
    print(my_list)

    # Python Dictionaries {} are key:value pairs
    
    # An empty dictionary
    my_dictionary = {}
    # Add a single key
    my_dictionary['color'] = 'blue'
    print(my_dictionary)

    my_dictionary = {'color':'blue','size':'large'}
    print(my_dictionary)

    tree = {'hieght':'100 feet', 'type': 'elm'}
    print(tree)

    # Mixed dictionaries

    my_dictionary = {'color':'blue','size':'large','tree': tree, 'mylist': my_list}
    print(my_dictionary)
    

    # Length
    list_len = len(my_list)
    dictionary_len = len(my_dictionary)
    print(list_len)
    print(dictionary_len)

    # Position
    print(my_list[3])  # Lists start at zero
    print(my_dictionary['tree']) # Dictionaries have keys
    print(f"The vale in the fourth position of my_list is {my_list[3]}")

    # Types
    list_type = type(my_list)
    disctionary_type= type(my_dictionary)
    print(list_type)
    print(disctionary_type)



except Exception as error:
    print('Ran into exception: exiting')


  
