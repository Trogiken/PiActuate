from enum import Enum


class GetAuto(str, Enum):
    sunrise_offset = "sunrise_offset"
    sunset_offset = "sunset_offset"
    active_sunrise = "active_sunrise"
    active_sunset = "active_sunset"
    active_current = "active_current"
    is_alive = "is_alive"


class PostAuto(str, Enum):
    sunrise_offset = "sunrise_offset"
    sunset_offset = "sunset_offset"
    start = "start"
    stop = "stop"
    refresh = "refresh"


class GetDoor(str, Enum):
    status = "status"


class PostDoor(int, Enum):
    open = 2
    close = 1


class GetAux(str, Enum):
    is_alive = "is_alive"


class PostAux(str, Enum):
    run_aux = "run_aux"
    stop_aux = "stop_aux"