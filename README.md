# Chicken Door Project
**Automatic door with webapp integration**

_Tested on the [RPI 4 B](https://www.raspberrypi.com/products/raspberry-pi-4-model-b/) using a [relay hat](https://thepihut.com/products/raspberry-pi-relay-board)_

## Requirements

[Imported Files](requirments.txt)

- Python 3.10+
- Anvil Runtime
  - `pip install anvil-app-server`

## Features
- Automated Operation
- Auxiliary Control Buttons
- Safety Switch To Halt Movement
- Online Program Controls
  - Enable/Disable Automation
  - Enable/Disable Auxiliary Buttons
  - Timing Offsets
  - Open and Close Buttons
  - Shutdown, Restart, and Reset (_Restart and Reset requires the program to [start at boot](#creating-a-service)_)

## App Config
**Program uses the "BCM" pin layout**

| Variable        | Purpose                                   |
|-----------------|-------------------------------------------|
| off_state[^1]   | Power setting of relay **off** state      |
| relay1          | Extending Motion                          |
| relay2          | Retracting Motion                         |
| switch1         | Extend Limit                              |
| switch2         | Retract Limit                             |
| switch3         | Path of door is blocked                   |
| switch4         | Aux switch for `relay1`                   |
| switch5         | Aux switch for `relay2`                   |
| timezone[^2]    | Time zone of hardware                     |
| longitude       | Longitudinal location of hardware         |
| latitude        | Latitudinal location of hardware          |
| travel_time[^3] | Allowed time for the door to be in motion |
| ipv4            | Ipv4 address of host system               |
| port[^4]        | Free port for webapp to run on            |
| key             | String of numbers and letters             |

## Logging Config
See the official python documentation [here](https://docs.python.org/3/library/logging.config.html)

When editing the logging config be sure to use correct syntax and formatting to avoid crashing

## Creating a Service
### Linux

#### 1. Create a service file
``sudo nano /usr/lib/systemd/system/SERVICE_NAME.service``

#### 2. Create Script
```
[Unit]
Description=Control door via webapp
After=multi-user.target

[Service]
Type=simple
ExecStart=/path/to/bin/python /path/to/app.py

[Install]
WantedBy=multi-user.target
```
#### 3. Enable the service
``sudo systemctl enable SERVICE_NAME``

#### 4. Start the service
``sudo systemctl start SERVICE_NAME``

[^1]: If **Off** state of relay is _true_ (Send Power), _false_ (No Power)
[^2]: US/Eastern, Europe/Amsterdam
[^3]: Find the movement rate of door and the distance it must travel. Add an additional 4 - 6 seconds
[^4]: Port forward this value on your router to expose it to the WAN
