from enum import Enum
from string import ascii_uppercase

UPLINK_CLIENT_KEY = "DLVI5O6VBFTJ5QVEZILJTYLN-FCSV6U7Z5JICT2KO-CLIENT"
COLS = ascii_uppercase[:10]


class SonoraColor(Enum):
    TERMINAL_PAPER = (0.9922, 0.9647, 0.8863, 1)
    SONORAN_SAGE = (0.6235, 0.7412, 0.6471, 1)
    SEDONA_SUNSET = (0.7725, 0.2902, 0.2902, 1)
    MOUSE_FUR = (0.8392, 0.8078, 0.7882, 1)
    DESERT_RAIN = (0.3216, 0.6392, 1.0, 1)

class SetupStatusInternal(Enum):
    PLAYER1_DONE = "PLAYER1_DONE"
    PLAYER2_DONE = "PLAYER2_DONE"


class SetupStatus(Enum):
    NEITHER = "NEITHER"
    YOU_DONE_OPP_NOT = "YOU_DONE_OPP_NOT"
    OPP_DONE_YOU_NOT = "OPP_DONE_YOU_NOT"
    COMPLETE = "COMPLETE"


class Status(Enum):
    SETUP = "SETUP"
    ACTIVE = "ACTIVE"
    COMPLETE = "COMPLETE"


class Key(Enum):
    ENTER = 40

