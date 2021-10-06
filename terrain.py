from vector import Vec2


class Terrain:
    def __init__(self, width: int, height: int, elevations):
        self.width = width
        self.height = height
        self.grid = []
        self.elevations = elevations
        for y in range(height):
            row = []
            for x in range(width):
                row.append([])
            self.grid.append(row)

    def put(self, cat: 'Cat'):
        """
        Not guaranteed to remove the cat from the previous position. Ideally, should be used in a new terrain object.
        """
        if self.is_position_valid(cat.position):
            self.grid[cat.position.y][cat.position.x].append(cat)

    def is_position_valid(self, v: Vec2):
        return 0 <= v.x < self.width and 0 <= v.y < self.height

    def __repr__(self):
        res = ''
        for y in range(self.height):
            for x in range(self.width):
                res += '{'
                res += f'ele: {self.elevations[y][x]}'
                res += str(self.grid[y][x])
                res += '} '
            res += '\n'
        return res
