import ast
import os
import toml
import logging.config
from pathlib import Path


class Initialization:
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
        Setup source.auto.Auto()
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
        """Constructs all necessary attributes for the Initialization object"""
        self._home = str(Path(__file__).resolve().parents[1])  # DEBUG Correct level?
        self._source = os.path.join(self._home, 'source')
        self._app_config_path = os.path.join(self._home, 'appConfig.conf')  # DEBUG
        self._log = None

        self.save = None
        self.door = None
        self.auto = None
        self.app_config = None

        self._start()

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
                'gpio': {'board_mode': str(), 'off_state': bool(), 'relay1': int(), 'relay2': int(), 'switch1': int(), 'switch2': int(),
                         'switch3': int(), 'switch4': int(), 'switch5': int()},
                'properties': {'timezone': str(), 'longitude': float(), 'latitude': float(), 'travel_time': int()},
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

            from source.disk import Save
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

            from source.door import Door
            self.door = Door(board_mode=io['board_mode'], off_state=io['off_state'], relay1=io['relay1'],
                             relay2=io['relay2'], sw1=io['switch1'], sw2=io['switch2'], sw3=io['switch3'],
                             sw4=io['switch4'], sw5=io['switch5'], travel_time=prop['travel_time'])
            self._log.info("Door object created")
        except BaseException:
            raise AttributeError("Problem Creating Door Object")

        try:  # Create Auto Object
            self._log.info('Creating Auto Object')

            from source.auto import Auto  # DEBUG Removed redundant data type declaration; verify functionality
            self.auto = Auto(door=self.door, zone=prop['timezone'],
                             latitude=prop['latitude'], longitude=prop['longitude'],
                             sunrise_offset=save_data['sunrise_offset'],
                             sunset_offset=save_data['sunset_offset'])
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
        self._log.info("Initializing...")

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

        self._log.info("Initialization Complete!")
