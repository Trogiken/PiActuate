"""
***Door control with WebApp integration***
GitHub: https://github.com/Trogiken/chicken-door
"""
import os
import logging.config
from source import startup


runtime = startup.Initialization()
log = logging.getLogger('root')


# region WebApp Functions
def run_auto():
    """Calls auto.run()"""
    log.debug("CALLED")
    runtime.auto.run()  # TODO Make this also change DATA value like change_rise


def stop_auto():
    """Calls auto.stop()"""
    log.debug("CALLED")
    runtime.auto.stop()  # TODO Make this also change DATA value like change_rise


def run_aux():
    """Calls door.run_aux()"""
    log.debug("CALLED")
    runtime.door.run_aux()  # TODO change value in DATA


def stop_aux():
    """Calls door.stop_aux()"""
    log.debug("CALLED")
    runtime.door.stop_aux()  # TODO change value in DATA


def change_rise(offset):
    """Calls auto.set_sunrise(offset), saves the new value"""
    log.debug("CALLED")
    runtime.auto.set_sunrise(offset)
    runtime.save.change('sunrise_offset', offset)


def change_set(offset):
    """Calls auto.set_sunset(offset), saves the new value"""
    log.debug("CALLED")
    runtime.auto.set_sunset(offset)
    runtime.save.change('sunset_offset', offset)


def refresh_auto():
    """Calls auto.refresh()"""
    log.debug("CALLED")
    runtime.auto.refresh()


def get_times():
    """Returns sunrise and sunset times in a dictionary"""
    log.debug("CALLED")
    return {'sunrise': runtime.auto.active_sunrise(),
            'sunset': runtime.auto.active_sunset()}


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


def rpi_status():
    """Called by WebApp to check if it still has connection to this program, Returns None"""
    # DEBUG How would this work locally
    return


def door_status():
    """Returns func call door.get_status()"""
    return runtime.door.get_status()


def reset_config():
    """"Calls save.reset()"""
    runtime.save.reset()
    return


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

    runtime.auto.stop()
    runtime.door.cleanup()

    if parm == 'program':
        raise SystemExit  # DEBUG Probably doesn't stop webapp and server
    else:
        os.system(f'sudo shutdown -{parm} now')


def move(opt):
    """Takes opt (1 or 2) and calls door.move(opt)"""
    log.debug("CALLED")
    runtime.door.move(opt)


def change(variable, value):  # TODO Remove this once other webapp functions replace its function
    """Calls save.change(variable, value)"""
    log.debug("CALLED")
    runtime.save.change(variable, value)
# endregions
