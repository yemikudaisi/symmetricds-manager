from enum import Enum

class GroupLinkOptions(Enum):
    PUSH = 'P'
    WAIT_FOR_PULL = 'W'
    ROUTE_ONLY = 'R'