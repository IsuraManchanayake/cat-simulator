import math


class Vec2:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

    def __add__(self, other: 'Vec2') -> 'Vec2':
        return Vec2(self.x + other.x, self.y + other.y)

    def __mul__(self, other: float) -> 'Vec2':
        return Vec2(self.x * other, self.y * other)

    def __sub__(self, other: 'Vec2') -> 'Vec2':
        return self + other * -1

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    __rmul__ = __mul__

    def norm(self):
        return (self.x * self.x + self.y * self.y) ** 0.5

    def unit(self):
        norm = self.norm()
        if norm == 0:
            return Vec2(0, 0)
        return (1 / self.norm()) * self

    def dot(self, other: 'Vec2'):
        return self.x * other.x + self.y * other.y

    def serialize(self):
        return dict(x=self.x, y=self.y)

    def __repr__(self):
        return f'{{x={round(self.x, 3)},y={round(self.y, 3)}}}'
        # return f'{{x={self.x:.2f},y={self.y:.2f}}}'
        # return f'Vec2{{x={self.x},y={self.y}}}'


def mapf(x, a, b, p, q):
    """
    maps x from range a, b to p, q
    """
    return ((x - a) / (b - a)) * (q - p) + p


def normal_factor(x):
    return math.exp(-x ** 2)
