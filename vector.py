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

    __rmul__ = __mul__

    def __repr__(self):
        return f'Vec2{{x={self.x},y={self.y}}}'
