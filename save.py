import os
import pickle


class Save:
    filename = "DATA.pkl"
    default_save = {
                    'automation_enabled': True,
                    'lon': -84.6805442,
                    'lat': 42.9150336,
                    'timezone': 'US/Eastern',
                    'sunrise_offset_enabled': False, 'sunrise_offset': 0,
                    'sunset_offset_enabled': False, 'sunset_offset': 0
                    }

    if not os.path.exists(filename):
        with open(filename, 'wb') as f:
            pickle.dump(default_save, f)

    def load(self):
        """Return save data in dictionary format"""
        with open(self.filename, 'rb') as r:
            data = pickle.load(r)
        return data

    def reset(self):
        """Change save data to default state"""
        with open(self.filename, 'wb') as w:
            pickle.dump(self.default_save, w)

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
            return 'Invalid Variable'

        with open(self.filename, 'wb') as w:
            pickle.dump(save_data, w)
