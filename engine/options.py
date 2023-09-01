from enum import Enum


class PostAuto(str, Enum):
    sunrise_offset = "sunrise_offset"
    sunset_offset = "sunset_offset"
    start = "start"
    stop = "stop"
    refresh = "refresh"


class PostDoor(int, Enum):
    open = 2
    close = 1


class PostAux(str, Enum):
    start = "start"
    stop = "stop"