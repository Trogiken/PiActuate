from django.core import serializers
from django.http import JsonResponse
from .models import SystemConfig, StartupConfig
import requests
import json

# TODO Improve docstrings
# TODO Add error handling for if the api cannot be reached
class ApiComms:
    """Class for communicating with the api"""
    api_url = "http://localhost:8002/"
    default_header = {'Content-Type': 'application/json'}


    def _get_request(self, endpoint="", headers=default_header):
        """Get request"""
        request = requests.get(url=ApiComms.api_url + endpoint, headers=headers)
        if request.status_code == 522:
            request = None
        return request

    def _post_request(self, endpoint, json=None, headers=default_header):
        """Post request"""
        request = requests.post(url=ApiComms.api_url + endpoint, headers=headers, json=json)
        if request.status_code == 522:
            request = None
        return request

    # BUG This is not working
    def configure(self):
        # Convert individual objects to dictionaries
        system_config_data = serializers.serialize("json", [SystemConfig.objects.first()])
        startup_config_data = serializers.serialize("json", [StartupConfig.objects.first()])

        # Convert serialized data to dictionaries
        system_config_data = json.loads(system_config_data)
        startup_config_data = json.loads(startup_config_data)

        data = {
            "system_config": system_config_data[0]['fields'],  # Extract fields from the serialized data
            "startup_config": startup_config_data[0]['fields']
        }

        return self._post_request("configure", json=data)
    
    def runtime_alive(self):
        """Spoof function to check if runtime is alive"""
        request = self._get_request("door") # Call endpoint that requires runtime
        if request is None:
            return False
        return True
    
    def destroy(self):
        """Destroy api"""
        return self._post_request("destroy")
    
    def get_auto(self):
        """Return auto data"""
        return self._get_request("auto")
    
    def get_aux(self):
        """Return aux data"""
        return self._get_request("aux")
    
    def get_door(self):
        """Return door data"""
        return self._get_request("door")
    
    def get_door_status(self):
        """Return door data"""
        return self._get_request("door").json()["data"]["status"] # TODO Error handling
    
    def get_aux_status(self):
        """Return aux data"""
        return self._get_request("aux").json()["data"]["is_alive"] # TODO Error handling
    
    def get_auto_status(self):
        """Return auto data"""
        return self._get_request("auto").json()["data"]["is_alive"] # TODO Error handling
    
    def close_door(self):
        """Close door"""
        return self._post_request("door?option=1")
    
    def open_door(self):
        """Open door"""
        return self._post_request("door?option=2")
    
    def alter_auto(self, key, value=None):  # DEBUG: None value might cause issues (Int expected)
        """Alter auto"""
        return self._post_request(f"auto?option={key}&value={value}")

    def alter_aux(self, key):
        """Alter aux"""
        return self._post_request(f"aux?option={key}")