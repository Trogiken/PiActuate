import ast
import os
import logging.config
from pathlib import Path

from controls.models import SystemConfig, StartupConfig


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
    system_config : dict
        System Config values
    startup_config : dict
        Startup Config values

    Methods
    -------
    _logging_config_load():
        Read and load logging config
    _is_rpi():
        Verify that system is an RPI
    _load_objects():
        Create and assign required objects to class variables while verifying functionality
    _start():
        Run the private methods in correct order
    """
    def __init__(self):
        """Constructs all necessary attributes for the Initialization object"""
        self._home = str(Path(__file__).resolve().parents[2])  # DEBUG Correct level?
        self._source = str(Path(__file__).resolve().parents[0])
        self._log = None

        self.door = None
        self.auto = None
        self.system_config = SystemConfig.objects.first()
        self.startup_config = StartupConfig.objects.first()

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

    def _load_objects(self):
        """Load system config and create objects, then run stored states (Load Last)"""
        
        self._log.debug(f"Loaded System Config Data: {self.system_config}")
        self._log.debug(f"Loaded Startup Config Data: {self.startup_config}")

        SyC = self.system_config
        StC = self.startup_config


        try:  # Create Door Object
            self._log.info('Creating Door Object')

            from source.door import Door
            self.door = Door(board_mode=SyC['board_mode'], off_state=SyC['off_state'], relay1=SyC['relay1'],
                             relay2=SyC['relay2'], sw1=SyC['switch1'], sw2=SyC['switch2'], sw3=SyC['switch3'],
                             sw4=SyC['switch4'], sw5=SyC['switch5'], travel_time=SyC['travel_time'])
            self._log.info("Door object created")
        except BaseException:
            raise AttributeError("Problem Creating Door Object")

        try:  # Create Auto Object
            self._log.info('Creating Auto Object')

            from source.auto import Auto  # DEBUG Removed redundant data type declaration; verify functionality
            self.auto = Auto(door=self.door, zone=SyC['timezone'],
                             latitude=SyC['latitude'], longitude=SyC['longitude'],
                             sunrise_offset=StC['sunrise_offset'],
                             sunset_offset=StC['sunset_offset']
                             )
            self._log.info("Automation object created")
        except BaseException:
            raise AttributeError("Problem Creating Auto Object")

        # Execute Saved States
        self._log.debug('Executing Saved States...')
        if StC['automation']:
            self._log.debug('Running Automation')
            self.auto.run()
        elif StC['auxiliary']:
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
