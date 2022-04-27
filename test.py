import yaml

with open('config.yaml') as f:
    loaded_config = yaml.safe_load(f)


class Config:
    @staticmethod
    def set_state(variable, value):
        with open('config.yaml') as file:
            data = yaml.safe_load(file)

        try:
            data[f'{variable}'] = value
        except ValueError as err:
            return err

        with open('config.yaml', 'w') as file:
            yaml.safe_dump(data, file)

        return True

    @staticmethod
    def get_state(state, variable=None, get_all=False):
        if state == 'current':
            with open('config.yaml') as file:
                data = yaml.safe_load(file)

            if get_all:
                return list(data.values())
            elif variable:
                return f"{variable} = {data[variable]}"
            else:
                return None
        elif state == 'loaded':
            if get_all:
                return list(loaded_config.values())
            elif variable:
                return f"{variable} = {loaded_config[variable]}"
            else:
                return None
        else:
            return f'Invalid State: {state}'

    def change(self, variable, value):
        valid_variables = list(loaded_config.keys())

        if variable in valid_variables:
            if variable == 'max_travel_time':
                try:
                    value = int(value)
                    self.set_state('max_travel_time', value)
                except ValueError:
                    return '[max_travel_time] Must be an Integer'
            elif variable == 'automation':
                if value == 'True':
                    value = True
                elif value == 'False':
                    value = False
                else:
                    return '[Automation] Must be True or False'
                self.set_state('automation', value)
            elif variable == 'latitude':
                try:
                    value = float(value)
                    self.set_state('latitude', value)
                except ValueError:
                    return '[Latitude] Must be an Float'
            elif variable == 'longitude':
                try:
                    value = float(value)
                    self.set_state('longitude', value)
                except ValueError:
                    return '[Longitude] Must be an Float'
            elif variable == 'timezone':
                if type(value) == str:
                    self.set_state('timezone', value)
                else:
                    return '[Timezone] Must be a String'
            elif variable == 'relay_1':
                try:
                    value = int(value)
                    self.set_state('relay_1', value)
                except ValueError:
                    return '[Relay 1] Must be an Integer'
            elif variable == 'relay_2':
                try:
                    value = int(value)
                    self.set_state('relay_2', value)
                except ValueError:
                    return '[Relay 2] Must be an Integer'
            elif variable == 'top_switch':
                try:
                    value = int(value)
                    self.set_state('top_switch', value)
                except ValueError:
                    return '[Top Switch] Must be an Integer'
            elif variable == 'bottom_switch':
                try:
                    value = int(value)
                    self.set_state('bottom_switch', value)
                except ValueError:
                    return '[Bottom Switch] Must be an Integer'
            elif variable == 'light_sensor':
                try:
                    value = int(value)
                    self.set_state('light_sensor', value)
                except ValueError:
                    return '[Light Sensor] Must be an Integer'
            else:
                raise ValueError("Make sure config variables are the same as the variables in change()")

            return f'[{variable}] set to [{value}]'
        else:
            return 'Invalid Variable'

