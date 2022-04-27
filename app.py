from door import Door
from automation import Auto
from configuration import Config
import anvil.server
import os
import yaml

# Set static IP for RPI
with open('config.yaml') as f:
    loaded_config = yaml.safe_load(f)

door = Door(relay1=loaded_config['relay_1'], relay2=loaded_config['relay_2'], top_switch=loaded_config['top_switch'],
            bottom_switch=loaded_config['bottom_switch'], light_sensor=loaded_config['light_sensor'],
            max_travel_time=loaded_config['max_travel_time'])
auto = Auto(door=door, zone=loaded_config['timezone'], latitude=loaded_config['latitude'], longitude=loaded_config['longitude'])
config = Config()


try:
    anvil.server.connect("V5QNUE3PMZD42P7RSPOVDGL5-PTAOXCGWB7VCBPZK")

    @anvil.server.background_task
    def run_auto():
        auto.run()

    if loaded_config['automation']:
        anvil.server.launch_background_task('run_auto')

    @anvil.server.callable
    def get_current_state(variable=None, get_all=False):
        return Config.get_state('current', variable, get_all)

    @anvil.server.callable
    def get_loaded_state(variable=None, get_all=False):
        return Config.get_state('loaded', variable, get_all)

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
        return door.move(direction)

    @anvil.server.callable
    def door_status():
        return door.status()

    @anvil.server.callable
    def change(variable, value):
        config.change(variable, value)


    anvil.server.wait_forever()
except Exception as err:
    if err == 'KeyboardInterrupt':
        anvil.server.disconnect()
    else:
        print(f"**** CRITICAL ERROR: {err} ****")
        anvil.server.disconnect()

    exit()
