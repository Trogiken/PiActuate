# Chicken Door Project
**Automatic door with webapp integration**

_Tested on the [RPI 4 B](https://www.raspberrypi.com/products/raspberry-pi-4-model-b/) using a [relay hat](https://thepihut.com/products/raspberry-pi-relay-board)_

## Requirements
Python 3.10+

[Imported Files](requirements.txt)

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
1. Download/Clone the Repository two subfolders deep `/home/Projects/DOOR-REPO/REPO`
  * This is so that the REPO.sock file is placed in the DOOR-REPO directory; for organization
2. Open a CLI session in the REPO directory
3. Set the environment variables in webenv: `nano ./webenv`
  * SECRET_KEY : Cryptographic signing and encryption throughout app.
    * Example: `SECRET_KEY="not-secure-key-)*j23891A0239("`
    * If none is given, a random one will be assigned each run
  * IS_DEVELOPMENT : Application will run with debug mode on.
    * Example: `IS_DEVELOPMENT="False"`
    * If none is given, will be set to True
  * ALLOWED_HOSTS : Valid host names Django can serve.
    * Example: `ALLOWED_HOSTS="192.1.1.1,172.200.20.1,hostname.com"`
    * If none is given, will be set to a wildcard
4. Run `chmod +x ./setup_script.sh && sudo ./setup_script.sh`

You're done!
3 Services (Nginx, Gunicorn, and Daphne) have been made that will start at boot and all dependancies have been neatly packed into a virtual environment in the REPO directory

_You may need to adjust the version of python or pip that is used such as changing python -> python3 and pip -> pip3_

## System Config

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

[^1]: If **Off** state of relay is _true_ (Send Power), _false_ (No Power)
[^2]: For a list of zones run the following: `import pytz`, then enter `pytz.all_timezones`
[^3]: Find the movement rate of door and the distance it must travel. Add an additional 4 - 6 seconds
[^4]: Port forward this value on your router to expose it to the WAN
