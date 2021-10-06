import random

from terrain import Terrain
from models import Cat
from vector import Vec2


class State:
    """
    Members:
        Input parameters:
            args
            start_from_file

        Simulation states i.e. should be serialized:
            width
            height
            seed
            n_steps
            step
            population
            terrain

    """
    def __init__(self, args):
        self.args = args
        self.start_from_file = self.args.state_file is not None

    def _start_from_file(self):
        pass

    def _start_from_parameters(self):
        self.seed = self.args.seed
        self.n_steps = self.args.n_steps
        self.population = self.args.population

        self.step = 0

        random.seed(self.seed)

        # Build elevations
        if self.args.t_elevation_file is None:
            elevations = [[0 for _ in range(self.args.t_width)] for __ in range(self.args.t_height)]
            self.height = self.args.t_height
            self.width = self.args.t_width
        else:
            with open(self.args.t_elevation_file, 'r') as ele_f:
                elevations = []
                width = -1
                for line in ele_f:
                    line = line.strip()
                    row = list(map(int, line.split(' ')))
                    if width == -1:
                        width = len(row)
                        if width == 0:
                            raise ValueError('Invalid elevation map.')
                    elif width != len(row):
                        raise ValueError('Invalid elevation map.')
                    elevations.append(row)
                if len(elevations) == 0:
                    raise ValueError('Invalid elevation map.')
                self.height = len(elevations)
                self.width = width

        # Build terrain
        self.terrain = Terrain(width=self.width, height=self.height, elevations=elevations)

        # Put cats on the terrain
        for i in range(self.population):
            x = random.randrange(0, self.terrain.width)
            y = random.randrange(0, self.terrain.height)
            cat = Cat(position=Vec2(x, y))
            self.terrain.put(cat=cat)

    def start(self):
        if self.start_from_file:
            self._start_from_file()
        else:
            self._start_from_parameters()

    def render(self):
        pass

    def serialize(self):
        pass

    def step(self):
        pass
