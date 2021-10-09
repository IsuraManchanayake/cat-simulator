from enum import IntEnum, Enum
from random import randrange


class RandomaziableEnum(Enum):
    def __str__(self):
        return self.name

    @classmethod
    def random(cls):
        val = randrange(0, len(cls))
        return cls(val)


class Gender(RandomaziableEnum):
    male = 0
    female = 1


class Personality(RandomaziableEnum):
    X = 0
    Y = 1


class State(RandomaziableEnum):
    fetus = 0
    active = 1
    sleeping = 2
    dead = 3


class CellType(RandomaziableEnum):
    floor = 0
    food = 1
    bed = 2
    box = 3


class Neighborhood(IntEnum):
    Moore = 0
    VonNeumann = 1


class LogMethod(IntEnum):
    none = 0
    console = 1
    file = 2
