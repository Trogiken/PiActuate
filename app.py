from door import Door
from automation import Auto
from save import Save
from base_logger import log
import anvil.server
import os

log.info("App Startup...")

# Set static IP for RPI
save = Save()
loaded_save = save.load()

log.info(f"Save Loaded - {loaded_save}")

sunrise_offset = 0
sunset_offset = 0
if loaded_save['sunrise_offset_enabled']:
    sunrise_offset = loaded_save['sunrise_offset']
if loaded_save['sunset_offset_enabled']:
    sunset_offset = loaded_save['sunset_offset']

door = Door(relay1=26, relay2=20, top_switch=0, bottom_switch=0, light_sensor=0, max_travel_time=10)
log.info("Door object created")

auto = Auto(door=door, zone=str(loaded_save['timezone']), latitude=float(loaded_save['lat']),
            longitude=float(loaded_save['lon']), sunrise_offset=int(sunrise_offset), sunset_offset=int(sunset_offset))
log.info("Automation object created")

try:
    anvil.server.connect("")
    log.info("Server Connection Made")

    @anvil.server.background_task
    def run_auto():
        auto.run()

    if loaded_save['automation_enabled']:
        anvil.server.launch_background_task('run_auto')
        log.info("Automation Enabled")
    else:
        log.info("Automation Disabled")

    @anvil.server.callable
    def get_current_state(variable=None):
        if variable is not None:
            return save.load()[variable]
        else:
            return save.load().values()

    @anvil.server.callable
    def get_loaded_state(variable=None):
        if variable is not None:
            return loaded_save[variable]
        else:
            return loaded_save.values()

    @anvil.server.callable
    def rpi_status():
        return

    @anvil.server.callable
    def restart():
        anvil.server.disconnect()
        os.system('python restart.py')
        exit()

    @anvil.server.callable
    def move(direction):
        # return door.move(direction)
        return

    @anvil.server.callable
    def door_status():
        # return door.status()
        return

    @anvil.server.callable
    def change(variable, value):
        return save.change(variable, value)


    anvil.server.wait_forever()
except Exception as err:
    if err == 'KeyboardInterrupt':
        anvil.server.disconnect()
    else:
        log.exception("Failure")
        anvil.server.disconnect()
        save.reset()
        os.system('python restart.py')

    exit()
