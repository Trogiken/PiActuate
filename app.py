from source.base_logger import log
log.info("App Startup...")

from source.door import Door
from source.auto import Auto
from source.save import Save
import anvil.server
import os

# Set static IP for RPI
save = Save()
loaded_save = save.load()
log.info("Save Loaded")
log.debug(f"Loaded Save Data: {loaded_save}")


sunrise_offset = loaded_save['sunrise_offset']
sunset_offset = loaded_save['sunset_offset']

door = Door(relay1=26, relay2=20, sw1=6, sw2=13, sw3=19, sw4=13, sw5=24, max_travel=10)
log.info("Door object created")

auto = Auto(door=door, zone=str(loaded_save['timezone']), latitude=float(loaded_save['lat']),
            longitude=float(loaded_save['lon']), sunrise_offset=int(sunrise_offset), sunset_offset=int(sunset_offset))
log.info("Automation object created")


ID = "NJVUFM2IX4WAT5SEHECJLQZ7-CLDWHXPSURNV4EW5"


def main():
    try:
        log.debug(f"Connection ID: {ID}")
        anvil.server.connect(f"{ID}")
        log.info("Server Connection Made")

        if loaded_save['automation_enabled']:
            auto.run()

        @anvil.server.callable
        def run_auto():
            log.debug("CALLED")
            auto.run()

        @anvil.server.callable
        def stop_auto():
            log.debug("CALLED")
            auto.stop()

        @anvil.server.callable
        def change_rise(offset):
            log.debug("CALLED")
            auto.sunrise_offset = offset
            save.change('sunrise_offset', offset)

        @anvil.server.callable
        def change_set(offset):
            log.debug("CALLED")
            auto.sunset_offset = offset
            save.change('sunset_offset', offset)

        @anvil.server.callable
        def times():
            log.debug("CALLED")
            return {'sunrise': auto.active_sunrise(),
                    'sunset': auto.active_sunset()}

        @anvil.server.callable
        def c_state(variable=None):
            log.debug("CALLED")
            if variable is not None:
                return save.load()[variable]
            else:
                return save.load()

        @anvil.server.callable
        def l_state(variable=None):
            log.debug("CALLED")
            if variable is not None:
                return loaded_save[variable]
            else:
                return loaded_save.values()

        @anvil.server.callable
        def rpi_status():
            return

        @anvil.server.callable
        def door_status():
            return door.get_status()

        @anvil.server.callable
        def restart():
            log.debug("CALLED")
            anvil.server.disconnect()
            os.system('python restart.py')
            exit()

        @anvil.server.callable
        def move(opt):
            log.debug("CALLED")
            return door.move(opt)

        @anvil.server.callable
        def change(variable, value):
            log.debug("CALLED")
            return save.change(variable, value)

        log.info("Startup Complete!")
        anvil.server.wait_forever()
    except Exception:
        log.exception("FAILURE")
        anvil.server.disconnect()

        exit()


if __name__ == '__main__':
    main()
