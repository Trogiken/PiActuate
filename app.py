# from door import Door
from datetime import datetime, timezone
import anvil.server
import yaml


# Set static IP for RPI
# Check for update button that pulls from GitHub
# Change max travel time
# Text Fields with background text like: max_travel_time: int
#   Then have a save button that changes variable values and saves it to a local file

# door = Door()
# @anvil.server.callable
# def move(direction):
#     return door.move(direction)

anvil.server.connect("V5QNUE3PMZD42P7RSPOVDGL5-PTAOXCGWB7VCBPZK")
with open('config.yaml') as f:
    config = yaml.safe_load(f)


@anvil.server.background_task
def automation():
    if config['automation'] is False:
        return
# anvil.server.launch_background_task('automation')


def set_state(variable, value):
    with open('config.yaml') as file:
        data = yaml.safe_load(file)

    data[f'{variable}'] = value

    with open('config.yaml', 'w') as file:
        yaml.safe_dump(data, file)


@anvil.server.callable
def restart():
    pass


@anvil.server.callable
def change(variable, value):  # Restart required for changes
    valid_variables = ['max_travel_time', 'relay_1', 'relay_2', 'automation', 'city', 'country',
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
        elif variable == 'city':
            if type(value) == 'str':
                set_state('city', value)
            else:
                return '[City] Must be a String'
        elif variable == 'country':
            if type(value) == 'str':
                set_state('country', value)
            else:
                return '[Country] Must be a String'
        elif variable == 'timezone':
            if type(value) == 'str':
                set_state('timezone', value)
            else:
                return '[Timezone] Must be a String'
        elif variable == 'relay_1':
            try:
                value = int(value)
                set_state('relay1', value)
            except ValueError:
                return '[Relay 1] Must be an Integer'
        elif variable == 'relay_2':
            try:
                value = int(value)
                set_state('relay2', value)
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
