# Chicken Door Project
Automatic door with [WebApp](https://CLDWHXPSURNV4EW5.anvil.app/YYX76UIW3FLUVCCLEB6FN5WL) integration

**Requires Python 3.10+**

## Features
- Automated Operation
- Timing Offsets
- Auxiliary Control Buttons
- Safety Switch To Hault Movement

## Config File
|Variable|Purpose|
|--------|--------|
|   install         | Path to program folder |
|   debug[^1]           | Debug Mode |
|   relay1          | Extending Motion |
|   relay2          | Retracting Motion |
|   switch1         | Extend Limit |
|   switch2         | Retract Limit |
|   switch3         | Path of door is blocked |
|   aux_switch1     | Trigger `relay1` |
|   aux_switch2     | Trigger `relay2` |
|   time_zone[^2]       | Time zone of hardware |
|   longitude       | Longitudinal location of hardware |
|   latitude        | Latitudinal location of hardware |
|   max_travel_time[^3] | Allowed time for the door to be in motion |
|   anvil_id        | Anvil Uplink ID |

## Creating a Service
### Linux
1. sudo nano /usr/lib/systemd/system/SERVICE_NAME.service
2. ```enter script``` Save File
3. sudo systemctl enable SERVICE_NAME
4. sudo systemctl start SERVICE_NAME

[^1]: Program will lower logging levels from **info** to **debug**
[^2]: US/Eastern, Europe/Amsterdam
[^3]: Find the movement rate of door and the distance it must travel. Add an additional 4 - 6 seconds
