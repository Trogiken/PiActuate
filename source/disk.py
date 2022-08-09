from .base_logger import log
import os
import pickle


class Save:
    """
    A class that manages save file

    ...

    Methods
    -------
    load():
        read file data
    reset():
        dump default save data into file
    change(variable="", value=""):
        change variable in file to value given
    """
    filename = "/home/pi/scripts/chicken-door/DATA.pkl"
    default_save = {
                    'automation': False,
                    'auxiliary': False,
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
        """
        Read file data

        returns
        -------
        data (dict)
        """
        with open(self.filename, 'rb') as r:
            data = pickle.load(r)
        log.debug("Save Read")
        return data

    def reset(self):
        """Dump default save data into file"""
        with open(self.filename, 'wb') as w:
            pickle.dump(self.default_save, w)
            log.info("Save Reset")

    def change(self, variable, value):
        """
        Change variable in file to value given

        Parameters
        ----------
        variable : str, required
            key in file to be changed
        value : (str, int, float, bool), required
            value of changed key
        """
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


class Config:
    def load(self):
        pass
