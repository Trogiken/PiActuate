import ast
import os
import logging.config
from pathlib import Path

# DEBUG Location change may cause logging issues
class Runtime(object):
    """
    Setup runtime objects and verify functionality

    ...

    Attributes
    ----------
    door : object
        Setup source.door.Door()
    auto : object
        Setup source.auto.Auto()
    system_config : class
        System Config values
    startup_config : class
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
    __shared_instance = None

    @staticmethod
    def getInstance():
        """Static Access Method"""
        return Runtime.__shared_instance
    
    def __init__(self, system_config=None, startup_config=None):
        """Constructs all necessary attributes for the Initialization object"""
        if system_config is None or startup_config is None:
            raise ValueError("System Config or Startup Config is None")

        self._home = str(Path(__file__).resolve().parents[2])
        self._source = str(Path(__file__).resolve().parents[0])
        self._log = None


        self.door = None
        self.auto = None
        self.system_config = system_config
        self.startup_config = startup_config

        self._start()
        Runtime.__shared_instance = self

    def _logging_config_load(self):
        """Init logging config (Load First)"""
        # DEBUG Possible bug with data type in logging config - https://github.com/Trogiken/chicken-door/projects/2#card-90279747
        logdir = os.path.join(self._home, 'logs')
        config = os.path.join(self._home, 'loggingConfig.conf')

        with open(config) as c:
            data = c.read()
            try:
                dict_config = ast.literal_eval(data)  # reconstruct into dictionary
            except BaseException as convertError:
                raise ValueError(f'Logging config format is invalid | {convertError}')

        if not os.path.exists(logdir):
            # deepcode ignore UpdateAPI: <Creates 1 sub dirctory in root path, not multiple subs>
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
    def _is_rpi():
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
        
        self._log.info(f"System Config: {self.system_config}")
        self._log.info(f"Startup Config: {self.startup_config}")

        SyC = self.system_config
        StC = self.startup_config


        try:  # Create Door Object
            self._log.info('Creating Door Object')

            from source.door import Door  # DEBUG Location changed
            self.door = Door(board_mode=str(SyC["board_mode"]), off_state=SyC["off_state"], relay1=int(SyC["relay1"]),
                             relay2=int(SyC["relay2"]), sw1=int(SyC["switch1"]), sw2=int(SyC["switch2"]), sw3=int(SyC["switch3"]),
                             sw4=int(SyC["switch4"]), sw5=int(SyC["switch5"]), travel_time=int(SyC["travel_time"]))
            self._log.info("Door object created")
        except BaseException:
            raise AttributeError("Problem Creating Door Object")

        try:  # Create Auto Object
            self._log.info('Creating Auto Object')

            from source.auto import Auto  # DEBUG Location Changed
            self.auto = Auto(door=self.door, zone=str(SyC["timezone"]),
                             latitude=float(SyC["latitude"]), longitude=float(SyC["longitude"]),
                             sunrise_offset=int(StC["sunrise_offset"]),
                             sunset_offset=int(StC["sunset_offset"]),
                             )
            self._log.info("Automation object created")
        except BaseException:
            raise AttributeError("Problem Creating Auto Object")

        # Execute Saved States
        self._log.debug('Executing Saved States...')
        if StC["automation"]:
            self._log.debug('Running Automation')
            self.auto.start()
        if StC["auxiliary"]:
            self._log.debug('Running Auxiliary Switches')
            self.door.run_aux()

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

    
    def destroy(self):
        """Shutdown the door and exit the program"""
        self._log.info("Destroying current initialization...")
        self.auto.stop()
        self.door.cleanup()
        self._log.info("Initialization destroyed!")
