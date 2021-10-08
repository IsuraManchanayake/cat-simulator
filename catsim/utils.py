import random
from zlib import crc32

from .enums import CellType
from .math import Vec2


def char_cell_type_map():
    return {
        '.': CellType.floor,
        'F': CellType.food,
        'B': CellType.bed,
        'b': CellType.box,
    }


def char_to_cell_type(value: str):
    return char_cell_type_map().get(value, CellType.floor)


def cell_type_to_char(value: CellType):
    return {
        val: key for key, val in char_cell_type_map().items()
    }.get(value, '.')


def random_cell_type_list(k):
    """
    :param k: Number of items in the returning list. Used for populating
    """
    cell_type_weights = {
        CellType.floor: 92,
        CellType.bed: 3,
        CellType.box: 2,
        CellType.food: 4,
    }
    weights = [cell_type_weights[cell_type] for cell_type in CellType]
    return random.choices(list(CellType), weights=weights, k=k)


def calc_force(magnitude: float, from_v: Vec2, to_v: Vec2):
    return magnitude * (to_v - from_v).unit()


def get_sleep_probability(cell_type, health):
    p = {
        CellType.floor: 0.4,
        CellType.bed: 0.7,
        CellType.box: 0.8,
        CellType.food: 0.1,
    }[cell_type]
    if health > 90:
        p *= 1.05
    return p


def max_health(age):
    if age < 1:
        return 50
    return 100


def cross(a: Vec2, b: Vec2):
    return a.x * b.y - a.y * b.x


def int_to_float_hash(a):
    s = str(a)
    return float(crc32(s.encode('utf-8')) & 0xffffffff) / 2 ** 32


def int_to_color_hash(a):
    f = int_to_float_hash
    return f(a), f(a * 2), f(3 * a - 1)