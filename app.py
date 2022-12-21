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
    """
    Setup runtime objects and verify functionality

    ...

    Attributes
    ----------
    save : object
        Setup source.disk.Save()
    door : object
        Setup source.door.Door()
    auto : object
        Setup source.auto.Auto
    app_config : dict
        Config values

    Methods
    -------
    _logging_config_load():
        Read and load logging config
    _is_rpi():
        Verify that system is an RPI
    _app_config_load():
        Verify  and read app config data
    _load_objects():
        Create and assign required objects to class variables while verifying functionality
    _start():
        Run the private methods in correct order
    """
    def __init__(self):
        """Constructs all necessary attributes for the _Initialization object"""
        os.chdir(os.path.dirname(__file__))
        self._home = os.getcwd()
        self._source = os.path.join(self._home, 'source')
        self._app_config_path = os.path.join(self._home, 'appConfig.conf')  # DEBUG
        self._log = None

        self.save = None
        self.door = None
        self.auto = None
        self.app_config = None

        self._start()  # DEBUG

    def _logging_config_load(self):
        """Init logging config (Load First)"""
        logdir = os.path.join(self._home, 'logs')
        config = os.path.join(self._home, 'loggingConfig.conf')

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

        self._log = logging.getLogger('root')

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
        values = toml.load(self._app_config_path)
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
                self._log.critical(f'Invalid Config Data {values}')
                raise ValueError('Config Error')

    def _load_objects(self):
        """Load app config and create objects, then run stored states (Load Last)"""
        try:  # Read AppConfig
            self._log.debug('Reading App Config')

            self.app_config = self._app_config_load()
            io = self.app_config['gpio']
            prop = self.app_config['properties']
            self._log.info("Config Loaded")
            self._log.debug(f"Loaded Config Data: {self.app_config}")
        except BaseException:
            raise AttributeError("Failed to load config data")

        try:  # Create Save Object
            self._log.info('Creating Save Object')

            from source import Save
            self.save = Save(filepath=os.path.join(self._source, 'DATA.pkl'))
            self._log.info("Save object created")
        except BaseException:
            raise AttributeError("Problem Creating Save Object")

        try:  # Read Save Data
            self._log.info('Reading Save Data')

            save_data = self.save.load()
            self._log.info("Save Loaded")
            self._log.debug(f"Loaded Save Data: {save_data}")
        except BaseException:
            raise AttributeError("Problem Reading Save Data")

        try:  # Create Door Object
            self._log.info('Creating Door Object')

            from source import Door
            self.door = Door(relay1=io['relay1'], relay2=io['relay2'], sw1=io['switch1'], sw2=io['switch2'],
                             sw3=io['switch3'], sw4=io['switch4'], sw5=io['switch5'], travel_time=prop['travel_time'])
            self._log.info("Door object created")
        except BaseException:
            raise AttributeError("Problem Creating Door Object")

        try:  # Create Auto Object
            self._log.info('Creating Auto Object')

            from source import Auto
            self.auto = Auto(door=self.door, zone=str(prop['timezone']),
                             latitude=float(prop['latitude']), longitude=float(prop['longitude']),
                             sunrise_offset=int(save_data['sunrise_offset']),
                             sunset_offset=int(save_data['sunset_offset']))
            self._log.info("Automation object created")
        except BaseException:
            raise AttributeError("Problem Creating Auto Object")

        self._log.debug('Executing Saved States...')
        if save_data['automation']:
            self._log.debug('Running Automation')
            self.auto.run()
        elif save_data['auxiliary']:
            self._log.debug('Running Auxiliary Switches')
            self.door.run_aux()
        else:
            self._log.debug('Nothing Executed!')

    def _start(self):
        """Run Tests"""
        self._logging_config_load()
        self._log.info("Startup...")

        try:
            self._is_rpi()
        except Exception:
            self._log.exception("Program is designed for RPI only!")
            raise

        try:
            self._load_objects()
        except Exception:
            self._log.exception("Error loading objects")
            raise


def run():
    """Start webapp and connect up-link functions"""
    runtime = _Initialization()
    log = logging.getLogger('root')
    net = runtime.app_config['network']
    ipv4 = net['ipv4']
    port = net['port']
    key = net['key']

    log.debug(f"ipv4: {ipv4}")
    log.debug(f"port: {port}")
    log.debug(f"key: {key}")

    log.info("Connecting to WebApp...")
    os.system(f"anvil-app-server --app Door_Control --origin http://{ipv4}:{port}/ --uplink-key={key}")
    sleep(10)
    anvil.server.connect(key, url=f"ws://localhost:{port}/_/uplink")
    log.info(f"Webapp connected on '{ipv4}:{port}'")

    # region WebApp Functions
    @anvil.server.callable()
    def run_auto():
        """Calls auto.run()"""
        log.debug("CALLED")
        runtime.auto.run()

    @anvil.server.callable()
    def stop_auto():
        """Calls auto.stop()"""
        log.debug("CALLED")
        runtime.auto.stop()

    @anvil.server.callable()
    def run_aux():
        """Calls door.run_aux()"""
        log.debug("CALLED")
        runtime.door.run_aux()

    @anvil.server.callable()
    def stop_aux():
        """Calls door.stop_aux()"""
        log.debug("CALLED")
        runtime.door.stop_aux()

    @anvil.server.callable()
    def change_rise(offset):
        """Calls auto.set_sunrise(offset), saves the new value"""
        log.debug("CALLED")
        runtime.auto.set_sunrise(offset)
        runtime.save.change('sunrise_offset', offset)

    @anvil.server.callable()
    def change_set(offset):
        """Calls auto.set_sunset(offset), saves the new value"""
        log.debug("CALLED")
        runtime.auto.set_sunset(offset)
        runtime.save.change('sunset_offset', offset)

    @anvil.server.callable()
    def refresh_auto():
        """Calls auto.refresh()"""
        log.debug("CALLED")
        runtime.auto.refresh()

    @anvil.server.callable()
    def get_times():
        """Returns sunrise and sunset times in a dictionary"""
        log.debug("CALLED")
        return {'sunrise': runtime.auto.active_sunrise(),
                'sunset': runtime.auto.active_sunset()}

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
        log.debug("CALLED")
        if variable is not None:
            return runtime.save.load()[variable]
        else:
            return runtime.save.load()

    @anvil.server.callable()
    def rpi_status():
        """Called by WebApp to check if it still has connection to this program, Returns None"""
        # DEBUG How would this work locally
        return

    @anvil.server.callable()
    def door_status():
        """Returns func call door.get_status()"""
        return runtime.door.get_status()

    @anvil.server.callable()
    def reset_config():
        """"Calls save.reset()"""
        runtime.save.reset()
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
            log.warning("Shutting Down...")
        elif parm == 'r':
            log.warning("Restarting...")
        elif parm == 'program':
            log.warning("Program is shutting down...")
        else:
            return

        runtime.door.stop_aux()
        runtime.auto.stop()
        runtime.door.cleanup()

        if parm == 'program':
            exit()
        else:
            os.system(f'sudo shutdown -{parm} now')

    @anvil.server.callable()
    def move(opt):
        """Takes opt (1 or 2) and calls door.move(opt)"""
        log.debug("CALLED")
        runtime.door.move(opt)

    @anvil.server.callable()
    def change(variable, value):
        """Calls save.change(variable, value)"""
        log.debug("CALLED")
        runtime.save.change(variable, value)
    # endregions

    anvil.server.wait_forever()
    log.info("Startup Complete!")


if __name__ == '__main__':
    run()
