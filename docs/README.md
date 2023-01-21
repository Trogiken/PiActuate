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

## Installation
1. Install Requirements
2. Download Repository
3. Run the following in repo directory: `anvil-app-server --app Door_Control` _This will download a large .jar_
4. Force quit the WebApp once it has finished starting
5. Now you can run the program directly from the command line or via a service

## Running
1. Open a terminal in the same directory that contains Door_Control
2. Run the following replacing capitalized words with proper values `anvil-app-server --app Door_Control --origin http://IPV4:PORT/`

## App Config

| Variable        | Purpose                                   |
|-----------------|-------------------------------------------|
| board_mode      | BCM or BOARD layout                       |
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
User=USER-NAME
ExecStart=path/to/anvil-app-server --app path/to/Door_Control --origin http://IPV4:PORT/

[Install]
WantedBy=multi-user.target
```
Use `locate anvil-app-server` to find the command location
#### 3. Enable the service
``sudo systemctl enable SERVICE_NAME``

#### 4. Start the service
``sudo systemctl start SERVICE_NAME``

[^1]: If **Off** state of relay is _true_ (Send Power), _false_ (No Power)
[^2]: For a list of zones run the following: `import pytz`, then enter `pytz.all_timezones`
[^3]: Find the movement rate of door and the distance it must travel. Add an additional 4 - 6 seconds
[^4]: Port forward this value on your router to expose it to the WAN
