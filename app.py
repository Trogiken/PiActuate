from door import Door
from datetime import datetime, timezone
import anvil.server
import yaml
import ephem


# Set static IP for RPI
# Check for update button that pulls from GitHub
# Change max travel time
# Text Fields with background text like: max_travel_time: int
#   Then have a save button that changes variable values and saves it to a local file

anvil.server.connect("V5QNUE3PMZD42P7RSPOVDGL5-PTAOXCGWB7VCBPZK")

door = Door()
fred = ephem.Observer()
fred.date = datetime.now(timezone.utc)

# @anvil.server.callable
# def move(direction):
#     return door.move(direction)


@anvil.server.background_task
def automation():
    pass


# anvil.server.launch_background_task('automation')


def set_state(variable, value):
    with open('config.yaml') as f:
        config = yaml.safe_load(f)

    config[f'{variable}'] = value

    with open('config', 'w') as f:
        yaml.safe_dump(config, f)


@anvil.server.callable
def restart():
    pass


@anvil.server.callable
def change(variable, value):  # Restart required for changes
    valid_variables = ['maximum_travel_time', 'RELAY1', 'RELAY2']
    if variable in valid_variables:
        if variable == 'maximum_travel_time':
            if type(value) == int:
                set_state('maximum_travel_time', value)
            else:
                return '[maximum_travel_time] Must be an Integer'
        elif variable == 'RELAY1':
            if type(value) == int:
                set_state('relay1', value)
            else:
                return '[RELAY1] Must be an Integer'
        elif variable == 'RELAY2':
            if type(value) == int:
                set_state('relay2', value)
            else:
                return '[RELAY2] Must be an Integer'
    else:
        return 'Invalid Variable'


anvil.server.wait_forever()
