# Chicken Door Project
**Automatic door with webapp integration**

_Tested on the [RPI 4 B](https://www.raspberrypi.com/products/raspberry-pi-4-model-b/) using a [relay hat](https://thepihut.com/products/raspberry-pi-relay-board)_

## Requirements
Python 3.10+

[Imported Files](requirments.txt)

## Features
- Automated Operation
- Auxiliary Control Buttons
- Safety Switch To Halt Movement
- Status of the doors position
- Online Program Controls
  - Enable/Disable Automation
  - Enable/Disable Auxiliary Buttons
  - Timing Offsets
  - Open and Close Buttons

## Installation and Start
1. Install Requirements
2. Download Repository
3. Open a terminal session in the repositorys directory, then run: `./startup_script.sh`

Click [here](#creating-a-service) if you wish this script to run at boot

_You may need to adjust the python version or make an absolute path in the startup script_

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
#### 1. Create a service file
``sudo nano /usr/lib/systemd/system/SERVICE_NAME.service``

#### 2. Create Script
```
[Unit]
Description=Door Control Service
After=multi-user.target

[Service]
Type=simple
User=USER-NAME
ExecStart=path/to/startup_script.sh

[Install]
WantedBy=multi-user.target
```
After saving this script run `sudo systemctl daemon-reload` to pick up the changes
#### 3. Enable the service
``sudo systemctl enable SERVICE_NAME``

Allows the service script to run at boot

#### 4. Start the service
``sudo systemctl start SERVICE_NAME``

Run the service

#### 5. Check the status
``sudo systemctl status SERVICE_NAME``

Show if the service is running or not

[^1]: If **Off** state of relay is _true_ (Send Power), _false_ (No Power)
[^2]: For a list of zones run the following: `import pytz`, then enter `pytz.all_timezones`
[^3]: Find the movement rate of door and the distance it must travel. Add an additional 4 - 6 seconds
[^4]: Port forward this value on your router to expose it to the WAN
