import os
import pickle
import logging

log = logging.getLogger('root')


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
    def __init__(self, filepath: str):
        self.filename = filepath

        self.default_save = {
            'automation': False,
            'auxiliary': False,
            'sunrise_offset': 0,
            'sunset_offset': 0
        }

        if not os.path.exists(self.filename):
            log.info("No save found, Creating one...")
            with open(self.filename, 'wb') as f:
                pickle.dump(self.default_save, f)
                log.info("Save Created")

    def load(self):
        """Read file data, return data (dict)"""
        with open(self.filename, 'rb') as r:
            data = pickle.load(r)
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
            with open(self.filename, 'wb') as w:
                pickle.dump(save_data, w)
                log.info(f"[{variable}] changed to [{value}]")
        else:
            log.error("Invalid Variable")
