from django.core import serializers
from django.http import JsonResponse
from .models import SystemConfig, StartupConfig
from pathlib import Path
from pyupgrader.utilities import helper
import pyupgrader
import requests
import json
import os

PYUPGRADER_URL = r"https://raw.githubusercontent.com/Trogiken/PiActuate/Pre-Production/.pyupgrader/"
LOCAL_PROJECT_PATH = str(Path(__file__).resolve().parents[2])


# TODO Improve docstrings
class ApiComms:
    """Class for communicating with the api"""
    api_url = "http://localhost:8002/"
    default_header = {'Content-Type': 'application/json'}

    def __init__(self):
        self._update_manager = None
        self.config_manager = helper.Config()
        self._configure_update_manager()
    
    def _configure_update_manager(self):
        """Configure update manager"""
        attempt = 1
        while attempt <= 3:
            try:
                self._update_manager = pyupgrader.UpdateManager(PYUPGRADER_URL, LOCAL_PROJECT_PATH)
            except Exception:
                pass
            else:
                break
            attempt += 1

    def _get_request(self, endpoint="", headers=default_header):
        """Get request"""
        request = requests.get(url=ApiComms.api_url + endpoint, headers=headers)
        if request.status_code != 200 and request.status_code != 522:
            # TODO Add error handling
            pass
        return request

    def _post_request(self, endpoint, json=None, headers=default_header):
        """Post request"""
        request = requests.post(url=ApiComms.api_url + endpoint, headers=headers, json=json)
        if request.status_code != 200 and request.status_code != 522:
            # TODO Add error handling
            pass
        return request

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
        if request.status_code == 522:
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
        data = {
            "option": 1
        }
        return self._post_request("door", json=data)
    
    def open_door(self):
        """Open door"""
        data = {
            "option": 2
        }
        return self._post_request("door", json=data)
    
    def alter_auto(self, key, value=0):  # DEBUG: If offset key used without value, value defaults to 0
        """Alter auto"""
        data = {
            "option": key,
            "value": value
        }
        return self._post_request(f"auto", json=data)

    def alter_aux(self, key):
        """Alter aux"""
        data = {
            "option": key
        }
        return self._post_request(f"aux", json=data)
    
    def check_update(self):
        """Check for updates - return mock data if exception occurs to prevent crashing the system"""
        local_config = self.config_manager.load_yaml(
            os.path.join(LOCAL_PROJECT_PATH, ".pyupgrader", "config.yaml")
        )
        mock_check_update = {
            'has_update': False,
            'local_version': local_config.get('version'),
            'web_version': None,
            'description': local_config.get('description'),
        }
        try:
            return self._update_manager.check_update()
        except Exception:
            if self._update_manager is None:
                self._configure_update_manager()  # Try to reconfigure the update manager
            return mock_check_update

    def prepare_update(self):
        """Update the system - handle exceptions"""
        if self._update_manager is None:
            self._configure_update_manager()  # Try to reconfigure the update manager
        return self._update_manager.prepare_update()

    def update(self, actions_file):
        """Update the system - handle exceptions"""
        if self._update_manager is None:
            self._configure_update_manager()  # Try to reconfigure the update manager
        self._update_manager.update(actions_file)
