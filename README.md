# Chicken Door Project
Automatic door with [WebApp](https://CLDWHXPSURNV4EW5.anvil.app/YYX76UIW3FLUVCCLEB6FN5WL) integration

**Requires Python 3.10+**

## Features
- Automated Operation
- Auxiliary Control Buttons
- Safety Switch To Hault Movement
- Online Program Controls
  - Enable/Disable Automation
  - Enable/Disable Auxiliary Buttons
  - Timing Offsets
  - Open and Close Buttons
  - Shutdown, Restart, and Reset (Restart requires the program to start at boot)

## App Config
**Program uses the "BCM" pin layout**

|Variable|Purpose|
|--------|--------|
|   relay1          | Extending Motion |
|   relay2          | Retracting Motion |
|   switch1         | Extend Limit |
|   switch2         | Retract Limit |
|   switch3         | Path of door is blocked |
|   switch4         | Aux switch for `relay1` |
|   switch5         | Aux switch for `relay2` |
|   timezone[^1]       | Time zone of hardware |
|   longitude       | Longitudinal location of hardware |
|   latitude        | Latitudinal location of hardware |
|   travel_time[^2] | Allowed time for the door to be in motion |
|   anvil_id        | Anvil Uplink ID |

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

[^1]: Program will lower logging levels from **info** to **debug**
[^2]: US/Eastern, Europe/Amsterdam
[^3]: Find the movement rate of door and the distance it must travel. Add an additional 4 - 6 seconds
