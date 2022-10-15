from .packages import toml
from pathlib import Path
import os
import pickle
import logging

log = logging.getLogger('root')

os.chdir(os.path.dirname(__file__))
_cwd = os.getcwd()
home = str(Path(_cwd).parents[0])


class Config:
    """
    A class that manages config file

    ...

    Methods
    -------
    load():
        read file data
    """
    path = os.path.join(home, 'appConfig.conf')

    # validate config data
    _values = toml.load(path)
    match _values:
        case {
            'gpio': {'relay1': int(), 'relay2': int(), 'switch1': int(), 'switch2': int(), 'switch3': int(), 'switch4': int(), 'switch5': int()},
            'properties': {'timezone': str(), 'longitude': float(), 'latitude': float(), 'travel_time': int(), 'anvil_id': str()}
        }:
            pass
        case _:
            log.critical(f'Invalid Config Data {_values}')
            raise ValueError('Config Error')

    def load(self):
        """Read file data, return (dict)"""
        return toml.load(self.path)


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
    filename = os.path.join(home, 'DATA.pkl')
    default_save = {
        'automation': False,
        'auxiliary': False,
        'sunrise_offset': 0,
        'sunset_offset': 0
    }

    if not os.path.exists(filename):
        with open(filename, 'wb') as f:
            pickle.dump(default_save, f)
            log.info("Save Created")

    def load(self):
        """Read file data, return data (dict)"""
        with open(self.filename, 'rb') as r:
            data = pickle.load(r)
        log.debug("Save Read")
        return data

    def reset(self):
        """Dump default save data into file"""
        with open(self.filename, 'wb') as w:
            pickle.dump(self.default_save, w)
            log.debug("Save Reset")

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
