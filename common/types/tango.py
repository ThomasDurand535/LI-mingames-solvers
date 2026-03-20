from enum import Enum
from typing import TypedDict


class TangoCellValEnum(Enum):
    MOON = "Moon"
    SUN = "Sun"
    EMPTY = "Empty"


class TangoCellSignEnum(Enum):
    NONE = "None"
    EQUAL = "Equal"
    CROSS = "Cross"


class TangoCell(TypedDict):
    value: TangoCellValEnum
    right: TangoCellSignEnum
    bottom: TangoCellSignEnum
