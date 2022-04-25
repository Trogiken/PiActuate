from door import Door
from automation import Auto
import anvil.server
import os
import yaml

with open('config.yaml') as f:
    loaded_config = yaml.safe_load(f)

door = Door(relay1=loaded_config['relay_1'], relay2=loaded_config['relay_2'], top_switch=loaded_config['top_switch'],
            bottom_switch=loaded_config['bottom_switch'], light_sensor=loaded_config['light_sensor'],
            max_travel_time=loaded_config['max_travel_time'])
auto = Auto(door=door, zone=loaded_config['timezone'], latitude=loaded_config['latitude'], longitude=loaded_config['longitude'])


try:
    # Set static IP for RPI
    # Check for update button that pulls from GitHub
    # Make a status timer that calls a function that returns the position

    # door = Door()
    # auto = Auto()
    #

    # @anvil.server.callable
    # def move(direction):
    #     return door.move(direction)

    anvil.server.connect("V5QNUE3PMZD42P7RSPOVDGL5-PTAOXCGWB7VCBPZK")

    @anvil.server.background_task
    def run_auto():
        auto.run()

    if loaded_config['automation']:
        anvil.server.launch_background_task('run_auto')


    def set_state(variable, value):
        with open('config.yaml') as file:
            data = yaml.safe_load(file)

        data[f'{variable}'] = value

        with open('config.yaml', 'w') as file:
            yaml.safe_dump(data, file)


    @anvil.server.callable
    def get_state(variable):
        return f"{variable} = {loaded_config[variable]}"


    @anvil.server.callable
    def test():  # used in status check
        return


    @anvil.server.callable
    def restart():
        anvil.server.disconnect()
        os.system('python restart.py')
        exit()


    @anvil.server.callable
    def change(variable, value):  # Restart required for changes
        valid_variables = ['max_travel_time', 'relay_1', 'relay_2', 'automation', 'latitude', 'longitude',
                           'top_switch', 'bottom_switch', 'timezone', 'light_sensor']
        if variable in valid_variables:
            if variable == 'max_travel_time':
                try:
                    value = int(value)
                    set_state('max_travel_time', value)
                except ValueError:
                    return '[max_travel_time] Must be an Integer'
            elif variable == 'automation':
                if value == 'True':
                    value = True
                elif value == 'False':
                    value = False
                else:
                    return '[Automation] Must be True or False'
                set_state('automation', value)
            elif variable == 'latitude':
                try:
                    value = float(value)
                    set_state('latitude', value)
                except ValueError:
                    return '[Latitude] Must be an Float'
            elif variable == 'longitude':
                try:
                    value = float(value)
                    set_state('longitude', value)
                except ValueError:
                    return '[Longitude] Must be an Float'
            elif variable == 'timezone':
                if type(value) == str:
                    set_state('timezone', value)
                else:
                    return '[Timezone] Must be a String'
            elif variable == 'relay_1':
                try:
                    value = int(value)
                    set_state('relay_1', value)
                except ValueError:
                    return '[Relay 1] Must be an Integer'
            elif variable == 'relay_2':
                try:
                    value = int(value)
                    set_state('relay_2', value)
                except ValueError:
                    return '[Relay 2] Must be an Integer'
            elif variable == 'top_switch':
                try:
                    value = int(value)
                    set_state('top_switch', value)
                except ValueError:
                    return '[Top Switch] Must be an Integer'
            elif variable == 'bottom_switch':
                try:
                    value = int(value)
                    set_state('bottom_switch', value)
                except ValueError:
                    return '[Bottom Switch] Must be an Integer'
            elif variable == 'light_sensor':
                try:
                    value = int(value)
                    set_state('light_sensor', value)
                except ValueError:
                    return '[Light Sensor] Must be an Integer'

            return f'[{variable}] set to [{value}]'
        else:
            return 'Invalid Variable'


    anvil.server.wait_forever()
except Exception as err:
    if err == 'KeyboardInterrupt':
        anvil.server.disconnect()
    else:
        print(f"**** CRITICAL ERROR: {err} ****")
        anvil.server.disconnect()
        os.system('python restart.py')

    exit()
