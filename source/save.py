from .base_logger import log
import os
import pickle


class Save:
    filename = "DATA.pkl"
    default_save = {
                    'automation_enabled': False,
                    'lon': -84.6805442,
                    'lat': 42.9150336,
                    'timezone': 'US/Eastern',
                    'sunrise_offset': 0,
                    'sunset_offset': 0
                    }

    if not os.path.exists(filename):
        with open(filename, 'wb') as f:
            pickle.dump(default_save, f)
            log.info("Save Created")

    def load(self):
        """Return save data in dictionary format"""
        with open(self.filename, 'rb') as r:
            data = pickle.load(r)
        log.debug("Save Read")
        return data

    def reset(self):
        """Change save data to default state"""
        with open(self.filename, 'wb') as w:
            pickle.dump(self.default_save, w)
            log.info("Save Reset")

    def change(self, variable, value):
        """Change variable value in saved data"""
        save_data = self.load()
        variable = variable.lower()

        if variable in save_data.keys():
            if variable == 'true':
                value = True
            elif variable == 'false':
                value = False

            save_data[variable] = value
        else:
            log.error("Invalid Variable")

        with open(self.filename, 'wb') as w:
            pickle.dump(save_data, w)
            log.info(f"[{variable}] changed to [{value}]")
