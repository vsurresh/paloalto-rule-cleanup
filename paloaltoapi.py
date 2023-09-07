import requests
import json
import xml.etree.ElementTree as ET

class PaloAltoAPI:
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.username = username
        self.password = password
        requests.packages.urllib3.disable_warnings()

    def get_key(self):
        query = {'type':'keygen', 'user':self.username, 'password':self.password}
        response = requests.get(f"{self.base_url}/api", params=query, verify=False)

        root = ET.fromstring(response.text)
        api_key = root.find(".//key").text
        return {'X-PAN-KEY': api_key}

    def build_url(self, endpoint, device_group, name=None):
        location = {'location': 'device-group', 'device-group': device_group}
        if device_group == 'shared':
            location = {'location': 'shared'}
        if name is not None:
            location['name'] = name
        return f"{self.base_url}/restapi/v10.2/{endpoint}", location

    def get_resource(self, endpoint, device_group):
        url, location = self.build_url(endpoint, device_group)
        headers = self.get_key()
        response = requests.get(url, params=location, verify=False, headers=headers)
        return response.json()['result']['entry']
    
    def create_resource(self, endpoint, device_group, payload, name):
        url, location = self.build_url(endpoint, device_group, name)
        headers = self.get_key()
        response = requests.post(url, params=location, verify=False, headers=headers, data=payload)
        return response.text
    
    def edit_resource(self, endpoint, device_group, payload, name):
        url, location = self.build_url(endpoint, device_group, name)
        headers = self.get_key()
        response = requests.put(url, params=location, verify=False, headers=headers, data=payload)
        return response.text

    def delete_resource(self, endpoint, device_group, name):
        url, location = self.build_url(endpoint, device_group, name)
        headers = self.get_key()
        response = requests.delete(url, params=location, verify=False, headers=headers)
        return response.text
