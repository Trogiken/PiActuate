"""
***Door control with WebApp integration***
GitHub: https://github.com/Trogiken/chicken-door
"""
import os
import ast
import logging.config
import toml
from pathlib import Path
from source import disk
from source import Door
from source import Auto


class Initialization:
    def __init__(self):
        os.chdir(os.path.dirname(__file__))
        _cwd = os.getcwd()
        self.home = str(Path(_cwd).parents[0])  # DEBUG According to final level change '0'
        self.source = os.path.join(self.home, 'source')
        self.app_config_path = os.path.join(self.home, 'appConfig.conf')  # DEBUG

        self.log = None
        self.save = None
        self.door = None
        self.auto = None
        self.app_config = None

    def _logging_config_load(self):
        """Init logging config (Load 1)"""
        logdir = os.path.join(self.home, 'logs')
        config = os.path.join(self.home, 'loggingConfig.conf')

        with open(config) as c:
            data = c.read()
            try:
                dict_config = ast.literal_eval(data)  # reconstruct into dictionary
            except BaseException as convertError:
                raise ValueError(f'Logging config format is invalid | {convertError}')

        if not os.path.exists(logdir):
            os.mkdir(logdir)

        try:
            filename = dict_config['handlers']['file']['filename']
            dict_config['handlers']['file']['filename'] = os.path.join(logdir, filename)
        except KeyError as keyError:
            raise KeyError(f"Could not find 'filename' | {keyError}")

        try:
            logging.config.dictConfig(dict_config)
        except BaseException as setupError:
            raise Exception(f"Logging setup failed | {setupError}")

        self.log = logging.getLogger('root')

    @staticmethod
    def _is_rpi():
        """Check if system is running on an RPI (Load 2)"""
        import io
        try:
            with io.open('/sys/firmware/devicetree/base/model', 'r') as model:
                if 'raspberry pi' not in model.read().lower():
                    OSError('Program made for RPI only')
        except IOError:
            OSError('Program made for RPI only')

    def _app_config_check(self):
        """Validate and Store Config Data (Load 3)"""
        values = toml.load(self.app_config_path)
        match values:
            case {
                'gpio': {'relay1': int(), 'relay2': int(), 'switch1': int(), 'switch2': int(), 'switch3': int(),
                         'switch4': int(), 'switch5': int()},
                'properties': {'timezone': str(), 'longitude': float(), 'latitude': float(), 'travel_time': int()}
            }:
                self.app_config = values
            case _:
                self.log.critical(f'Invalid Config Data {values}')
                raise ValueError('Config Error')

        return values

    def load_objects(self):
        """Load config and create objects, then run stored states (Load 2)"""
        self._app_config_check()

        self.save = disk.Save(os.path.join(self.source, 'DATA.pkl'))
        self.log.debug("Save object created")

        loaded_save = self.save.load()
        self.log.info("Save Loaded")
        self.log.debug(f"Loaded Save Data: {loaded_save}")

        io = self.app_config['gpio']
        prop = self.app_config['properties']
        self.log.info("Config Loaded")
        self.log.debug(f"Loaded Config Data: {self.app_config}")

        self.door = Door(relay1=io['relay1'], relay2=io['relay2'], sw1=io['switch1'], sw2=io['switch2'],
                         sw3=io['switch3'], sw4=io['switch4'], sw5=io['switch5'], travel_time=prop['travel_time'])
        self.log.debug("Door object created")

        self.auto = Auto(door=self.door, zone=str(prop['timezone']),
                         latitude=float(prop['latitude']), longitude=float(prop['longitude']),
                         sunrise_offset=int(loaded_save['sunrise_offset']),
                         sunset_offset=int(loaded_save['sunset_offset']))
        self.log.debug("Automation object created")

        # Execute stored states
        if loaded_save['automation']:
            self.auto.run()
        if loaded_save['auxiliary']:
            self.door.run_aux()

    def run(self):
        """Run Tests"""
        self._logging_config_load()
        self.log.info("Startup...")

        self._is_rpi()
        self.load_objects()

        self.log.info("Startup Complete!")


class App(Initialization):
    def __init__(self):
        super().__init__()
        init = Initialization()
        init.run()

    def run(self):
        # TODO Have this run anvil runtime command with properties form app_config
        pass

    def run_auto(self):
        """Calls auto.run()"""
        self.log.debug("CALLED")
        self.auto.run()

    def stop_auto(self):
        """Calls auto.stop()"""
        self.log.debug("CALLED")
        self.auto.stop()

    def run_aux(self):
        """Calls door.run_aux()"""
        self.log.debug("CALLED")
        self.door.run_aux()

    def stop_aux(self):
        """Calls door.stop_aux()"""
        self.log.debug("CALLED")
        self.door.stop_aux()

    def change_rise(self, offset):
        """Calls auto.set_sunrise(offset), saves the new value"""
        self.log.debug("CALLED")
        self.auto.set_sunrise(offset)
        self.save.change('sunrise_offset', offset)

    def change_set(self, offset):
        """Calls auto.set_sunset(offset), saves the new value"""
        self.log.debug("CALLED")
        self.auto.set_sunset(offset)
        self.save.change('sunset_offset', offset)

    def refresh_auto(self):
        """Calls auto.refresh()"""
        self.log.debug("CALLED")
        self.auto.refresh()

    def get_times(self):
        """Returns sunrise and sunset times in a dictionary"""
        self.log.debug("CALLED")
        return {'sunrise': self.auto.active_sunrise(),
                'sunset': self.auto.active_sunset()}

    def c_state(self, variable=None):
        """
        Read save file

            Parameters:
                variable (str), optional: key in dictionary

            Returns:
                save.load() (dict): all data
                save.load()[variable] (str, int, float, bool): value of specified key
        """
        self.log.debug("CALLED")
        if variable is not None:
            return self.save.load()[variable]
        else:
            return self.save.load()

    def rpi_status(self):
        """Called by WebApp to check if it still has connection to this program, Returns None"""
        # DEBUG How would this work locally
        return

    def door_status(self):
        """Returns func call door.get_status()"""
        return self.door.get_status()

    def reset_config(self):
        """"Calls save.reset()"""
        self.save.reset()
        return

    def shutdown(self, parm='h'):
        """
        Shutdown or Restart system

        If parm is changed to 'r' the system will restart

            Parameters:
                parm (str), optional: Shutdown flag
        """
        if parm == 'h':
            self.log.warning("Shutting Down...")
        elif parm == 'r':
            self.log.warning("Restarting...")
        else:
            return

        self.stop_aux()
        self.stop_auto()
        self.door.cleanup()
        os.system(f'sudo shutdown -{parm} now')

    def move(self, opt):
        """Takes opt (1 or 2) and calls door.move(opt)"""
        self.log.debug("CALLED")
        self.door.move(opt)

    def change(self, variable, value):
        """Calls save.change(variable, value)"""
        self.log.debug("CALLED")
        self.save.change(variable, value)


if __name__ == '__main__':
    app = App()
    app.run()
