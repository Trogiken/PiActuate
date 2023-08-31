import requests


class ApiComms:
    """Class for communicating with the api"""

    def __init__(self):
        self.api_url = "http://localhost:8002/"
        self.headers = {'Content-Type': 'application/json'} # DEBUG 
    
    def _get_request(self, endpoint=""):
        """Get request"""
        return requests.get(url=self.api_url + endpoint, headers=self.headers)

    def _post_request(self, endpoint, data=None):
        """Post request"""
        return requests.post(url=self.api_url + endpoint, headers=self.headers, data=data)

    def configure(self, system_config, startup_config):
        """Configure api"""
        data = {
            "system_config": system_config,
            "startup_config": startup_config
        }
        return self._post_request("configure", data=data)  # DEBUG
    
    def destroy(self):
        """Destroy api"""
        return self._post_request("destroy")
    
    def get_auto(self):
        """Return auto data"""
        return self._get_request("auto")
    
    def get_door(self):
        """Return door data"""
        return self._get_request("door")
    
    def get_aux(self):
        """Return aux data"""
        return self._get_request("aux")
    
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