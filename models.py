from vector import Vec2


class Cat:
    _count = 0

    def __init__(self, position: Vec2):
        self.id = self._count
        self.position = position
        self._count += 1

    def move(self, distance: Vec2):
        self.position += distance

    @staticmethod
    def speak():
        return 'Meow'

    def __repr__(self):
        return f'Cat{{position={self.position}}}'
