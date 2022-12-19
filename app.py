"""
***Door control with WebApp integration***
GitHub: https://github.com/Trogiken/chicken-door
"""
import os
import ast
import logging.config
import anvil
import toml
from time import sleep


class _Initialization:
    def __init__(self):
        os.chdir(os.path.dirname(__file__))
        self.home = os.getcwd()
        self.source = os.path.join(self.home, 'source')
        self.app_config_path = os.path.join(self.home, 'appConfig.conf')  # DEBUG

        self.log = None
        self.save = None
        self.door = None
        self.auto = None
        self.app_config = None

        self._start()  # DEBUG

    def _logging_config_load(self):
        """Init logging config (Load First)"""
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
    def _is_rpi():  # DEBUG Method of identifying OS is untested
        """Check if system is running on an RPI"""
        import io

        is_rpi = True

        try:
            with io.open('/sys/firmware/devicetree/base/model', 'r') as model:
                if 'raspberry pi' not in model.read().lower():
                    is_rpi = False
        except IOError:
            is_rpi = False

        if not is_rpi:
            raise OSError("System is not recognized as RPI")

    def _app_config_load(self):
        """Validate and return config data"""
        values = toml.load(self.app_config_path)
        # TODO Check for empty elements
        match values:
            case {
                'gpio': {'relay1': int(), 'relay2': int(), 'switch1': int(), 'switch2': int(), 'switch3': int(),
                         'switch4': int(), 'switch5': int()},
                'properties': {'timezone': str(), 'longitude': float(), 'latitude': float(), 'travel_time': int()},
                'network': {'ipv4': str(), 'port': str(), 'key': str()}
            }:
                return values
            case _:
                self.log.critical(f'Invalid Config Data {values}')
                raise ValueError('Config Error')

    def _load_objects(self):
        """Load app config and create objects, then run stored states (Load Last)"""
        try:  # Read AppConfig
            self.log.debug('Reading App Config')

            self.app_config = self._app_config_load()
            io = self.app_config['gpio']
            prop = self.app_config['properties']
            self.log.info("Config Loaded")
            self.log.debug(f"Loaded Config Data: {self.app_config}")
        except BaseException:
            raise AttributeError("Failed to load config data")

        try:  # Create Save Object
            self.log.info('Creating Save Object')

            from source import Save
            self.save = Save(os.path.join(self.source, 'DATA.pkl'))
            self.log.info("Save object created")
        except BaseException:
            raise AttributeError("Problem Creating Save Object")

        try:  # Read Save Data
            self.log.info('Reading Save Data')

            save_data = self.save.load()
            self.log.info("Save Loaded")
            self.log.debug(f"Loaded Save Data: {save_data}")
        except BaseException:
            raise AttributeError("Problem Reading Save Data")

        try:  # Create Door Object
            self.log.info('Creating Door Object')

            from source import Door
            self.door = Door(relay1=io['relay1'], relay2=io['relay2'], sw1=io['switch1'], sw2=io['switch2'],
                             sw3=io['switch3'], sw4=io['switch4'], sw5=io['switch5'], travel_time=prop['travel_time'])
            self.log.info("Door object created")
        except BaseException:
            raise AttributeError("Problem Creating Door Object")

        try:  # Create Auto Object
            self.log.info('Creating Auto Object')

            from source import Auto
            self.auto = Auto(door=self.door, zone=str(prop['timezone']),
                             latitude=float(prop['latitude']), longitude=float(prop['longitude']),
                             sunrise_offset=int(save_data['sunrise_offset']),
                             sunset_offset=int(save_data['sunset_offset']))
            self.log.info("Automation object created")
        except BaseException:
            raise AttributeError("Problem Creating Auto Object")

        self.log.debug('Executing Saved States...')
        if save_data['automation']:
            self.log.debug('Running Automation')
            self.auto.run()
        elif save_data['auxiliary']:
            self.log.debug('Running Auxiliary Switches')
            self.door.run_aux()
        else:
            self.log.debug('Nothing Executed!')

    def _start(self):
        """Run Tests"""
        self._logging_config_load()
        self.log.info("Startup...")  # TODO Startup log messages are scattered

        try:
            self._is_rpi()
        except Exception:
            self.log.exception("Program is designed for RPI only!")
            raise

        try:
            self._load_objects()
        except Exception:
            self.log.exception("Error loading objects")
            raise


class App:
    def __init__(self):
        self.runtime = _Initialization()
        self.log = logging.getLogger('root')

        net = self.runtime.app_config['network']
        self.ipv4 = net['ipv4']
        self.port = net['port']
        self.key = net['key']

        self.log.debug(f"ipv4: {self.ipv4}")
        self.log.debug(f"port: {self.port}")
        self.log.debug(f"key: {self.key}")

        os.system(f"anvil-app-server --app Door_Control --origin http://{self.ipv4}:{self.port}/ --uplink-key={self.key}")
        sleep(10)

    def connect(self):

        self.log.info("Connecting to WebApp...")
        anvil.server.connect(self.key, url=f"ws://localhost:{self.port}/_/uplink")
        self.log.info(f"Webapp connected on '{self.ipv4}:{self.port}'")

        # TODO Link shutdown program button from webapp
        @anvil.server.callable()
        def run_auto():
            """Calls auto.run()"""
            self.log.debug("CALLED")
            self.runtime.auto.run()

        @anvil.server.callable()
        def stop_auto():
            """Calls auto.stop()"""
            self.log.debug("CALLED")
            self.runtime.auto.stop()

        @anvil.server.callable()
        def run_aux():
            """Calls door.run_aux()"""
            self.log.debug("CALLED")
            self.runtime.door.run_aux()

        @anvil.server.callable()
        def stop_aux():
            """Calls door.stop_aux()"""
            self.log.debug("CALLED")
            self.runtime.door.stop_aux()

        @anvil.server.callable()
        def change_rise(offset):
            """Calls auto.set_sunrise(offset), saves the new value"""
            self.log.debug("CALLED")
            self.runtime.auto.set_sunrise(offset)
            self.runtime.save.change('sunrise_offset', offset)

        @anvil.server.callable()
        def change_set(offset):
            """Calls auto.set_sunset(offset), saves the new value"""
            self.log.debug("CALLED")
            self.runtime.auto.set_sunset(offset)
            self.runtime.save.change('sunset_offset', offset)

        @anvil.server.callable()
        def refresh_auto():
            """Calls auto.refresh()"""
            self.runtime.log.debug("CALLED")
            self.runtime.auto.refresh()

        @anvil.server.callable()
        def get_times():
            """Returns sunrise and sunset times in a dictionary"""
            self.log.debug("CALLED")
            return {'sunrise': self.runtime.auto.active_sunrise(),
                    'sunset': self.runtime.auto.active_sunset()}

        @anvil.server.callable()
        def c_state(variable=None):
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
                return self.runtime.save.load()[variable]
            else:
                return self.runtime.save.load()

        @anvil.server.callable()
        def rpi_status():
            """Called by WebApp to check if it still has connection to this program, Returns None"""
            # DEBUG How would this work locally
            return

        @anvil.server.callable()
        def door_status():
            """Returns func call door.get_status()"""
            return self.runtime.door.get_status()

        @anvil.server.callable()
        def reset_config():
            """"Calls save.reset()"""
            self.runtime.save.reset()
            return

        @anvil.server.callable()
        def shutdown(parm='h'):
            """
            Shutdown or Restart system

            If parm is changed to 'r' the system will restart
            If parm is changed to 'program' the program will exit

                Parameters:
                    parm (str), optional: Shutdown flag
            """
            if parm == 'h':
                self.log.warning("Shutting Down...")
            elif parm == 'r':
                self.log.warning("Restarting...")
            elif parm == 'program':
                self.log.warning("Program is shutting down...")
            else:
                return

            self.runtime.door.stop_aux()
            self.runtime.auto.stop()
            self.runtime.door.cleanup()

            if parm == 'program':
                exit()
            else:
                os.system(f'sudo shutdown -{parm} now')

        @anvil.server.callable()
        def move(opt):
            """Takes opt (1 or 2) and calls door.move(opt)"""
            self.log.debug("CALLED")
            self.runtime.door.move(opt)

        @anvil.server.callable()
        def change(variable, value):
            """Calls save.change(variable, value)"""
            self.log.debug("CALLED")
            self.runtime.save.change(variable, value)

        anvil.server.wait_forever()
        self.log.info("Startup Complete!")


if __name__ == '__main__':
    app = App()
    app.connect()
