from typing import List

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from .config import Config
from .math import Vec2
from .enums import Personality, CellType, Neighborhood
from .models import Cat
from .utils import cross, cell_type_to_char, int_to_color_hash


class Cell:
    def __init__(self, position: Vec2, cats, x_trace=0.0, y_trace=0.0, cell_type=CellType.floor, food_amount=0.0,
                 elevation=0):
        self.position = position
        self.cats = cats
        self.x_trace = x_trace  # Trace of smell of x personality
        self.y_trace = y_trace  # Trace of smell of y personality
        self.cell_type = cell_type
        self.food_amount = food_amount
        self.elevation = elevation

    def increment_trace(self, personality: Personality, value: float):
        if personality == Personality.X:
            self.x_trace = min(Config.max_trace, self.x_trace + value)
        else:
            self.y_trace = min(Config.max_trace, self.y_trace + value)

    def put_cat(self, cat: 'Cat'):
        self.cats.append(cat)
        self.increment_trace(cat.personality, 1)

    def get_consumed(self, consumed_amount):
        self.food_amount = max(0, self.food_amount - consumed_amount)

    def annot(self):
        s = ''
        s += f'{self.position}'
        s += f'{len(self.cats)} cats, cell_type={self.cell_type},\n'
        s += f'elevation={self.elevation}\n'
        s += f'x_trace={self.x_trace:.2f}, y=trace={self.y_trace:.2f}\n'
        if self.cell_type == CellType.food:
            s += f'food_amount={self.food_amount}\n'
        for cat in self.cats:
            s += cat.annot() + '\n'
        return s

    def __repr__(self):
        return f'Cell{{position={self.position},cats={str(self.cats)},x_trace={self.x_trace},y_trace={self.y_trace},' \
               f'cell_type={self.cell_type},food_amount={self.food_amount},elevation={self.elevation}}}'


class Terrain:
    def __init__(self, width: int, height: int, elevations, cell_types, previous_terrain=None):
        self.width = width
        self.height = height
        self.grid = []
        self.elevations = elevations
        for y in range(height):
            row = []
            for x in range(width):
                if previous_terrain is not None:
                    food_amount = previous_terrain.grid[y][x].food_amount
                    x_trace = previous_terrain.grid[y][x].x_trace * Config.trace_fading_factor
                    y_trace = previous_terrain.grid[y][x].y_trace * Config.trace_fading_factor
                else:
                    food_amount = Config.start_food_amount if cell_types[y][x] == CellType.food else 0
                    x_trace, y_trace = 0, 0
                cell = Cell(
                    position=Vec2(x, y),
                    cats=[],
                    cell_type=cell_types[y][x],
                    elevation=elevations[y][x],
                    food_amount=food_amount,
                    x_trace=x_trace,
                    y_trace=y_trace,
                )
                row.append(cell)
            self.grid.append(row)

    def put_cat(self, cat: 'Cat'):
        """
        Not guaranteed to remove the cat from the previous position.
        Ideally, should be used on a new terrain object.
        """
        if self.is_position_valid(cat.position):
            self.cell_at(cat.position).put_cat(cat)

    def is_position_valid(self, v: Vec2):
        return 0 <= v.x < self.width and 0 <= v.y < self.height

    def at(self, x, y) -> Cell:
        return self.grid[y][x]

    def cell_at(self, pos: Vec2) -> Cell:
        return self.grid[pos.y][pos.x]

    def cats_at(self, pos: Vec2):
        return self.cell_at(pos).cats

    def neighbors(self, center: Vec2, r: int, neighborhood: Neighborhood) -> List[Cell]:
        if neighborhood == Neighborhood.Moore:
            positions = [center + Vec2(dx, dy) for dy in range(-r, r + 1) for dx in range(-r, r + 1)]
        else:
            positions = [center + Vec2(dx, dy) for dy in range(-r, r + 1) for dx in range(-r, r + 1) if
                         abs(dx) + abs(dy) <= r]
        valid_positions = [pos for pos in positions if self.is_position_valid(pos)]
        return [self.cell_at(pos) for pos in valid_positions]

    def health_damange_to_travel(self, from_pos: Vec2, to_pos: Vec2):
        elevation_difference = self.cell_at(to_pos).elevation - self.cell_at(from_pos).elevation
        return max(0, elevation_difference) + (to_pos - from_pos).norm()

    def _clamp(self, from_vec, to_vec):
        boundaries = [
            [Vec2(0, 0), Vec2(self.width - 1, 0)],
            [Vec2(0, 0), Vec2(0, self.height - 1)],
            [Vec2(self.width - 1, self.height - 1), Vec2(-self.width + 1, 0)],
            [Vec2(self.width - 1, self.height - 1), Vec2(0, -self.height + 1)],
        ]
        p, r = from_vec, to_vec - from_vec
        for q, s in boundaries:
            q_p = q - p
            q_pxr = cross(q_p, r)
            q_pxs = cross(q_p, s)
            rxs = cross(r, s)
            if q_pxr == 0.0:
                # Co-linear
                u1 = (p + r - q).dot(s) / s.dot(s)
                if u1 < 0:
                    return q
                elif u1 <= 1:
                    return p + r
                else:
                    return q + s
            if rxs == 0.0:
                continue  # Parallel, No intersection
            u = q_pxr / rxs
            t = q_pxs / rxs
            if 0 <= u <= 1 and 0 <= t <= 1:
                return p + r * t  # If intersects, return
        return p + r  # Intersects with none. All good!

    def make_lattice(self, v: Vec2):
        x = round(max(0, min(v.x, self.width - 1)))
        y = round(max(0, min(v.y, self.height - 1)))
        return Vec2(x, y)

    def clamp(self, from_vec: Vec2, to_vec: Vec2):
        """
        CLamp the target position by the boundaries
        :param from_vec: from vector
        :param to_vec: to vector
        """
        return self.make_lattice(self._clamp(from_vec, to_vec))

    def console_render(self):
        cell_w = 5
        cell_h = 3
        res = ''
        res += '+' + ('-' * cell_w + '+') * self.width + '\n'
        for y in range(self.height):
            res += '|'
            for x in range(self.width):
                cell = self.at(x, y)
                res += f'{cell_type_to_char(cell.cell_type):{cell_w}}' + '|'
            res += '\n'
            res += '|'
            for x in range(self.width):
                cell = self.at(x, y)
                s = ''
                if len(cell.cats) > 0:
                    s = f'c{len(cell.cats)}'
                res += f'{s:{cell_w}}' + '|'
            res += '\n'
            res += (('|' + (' ' * cell_w + '|') * self.width + '\n') * (cell_h - 2))
            res += '+' + ('-' * cell_w + '+') * self.width + '\n'
        # res += ((('|' + (' ' * cell_w + '|') * self.width + '\n') * cell_h) + '+' + ('-' * cell_w + '+') *
        # self.width + '\n') * self.height
        return res

    def render(self):
        xvalues = []
        yvalues = []
        cat_colors = []
        cell_colors = []
        for y in range(self.height):
            cell_color_row = []
            for x in range(self.width):
                cell = self.grid[y][x]
                cell_color_row.append(int_to_color_hash(cell.cell_type.value))
                for cat in cell.cats:
                    xvalues.append(x)
                    yvalues.append(y)
                    cat_colors.append(int_to_color_hash(cat.cat_id))
            cell_colors.append(cell_color_row)

        ax = plt.gca()
        for y in range(self.height - 1):
            ax.axhline(y + 0.5, linestyle='-', lw=0.5, alpha=0.3)
        for x in range(self.width - 1):
            ax.axvline(x + 0.5, linestyle='-', lw=0.5, alpha=0.3)

        sc = plt.scatter(xvalues, yvalues, c=cat_colors)

        # ax.axes.xaxis.set_visible(False)
        # ax.axes.yaxis.set_visible(False)

        for tick in [*ax.xaxis.get_major_ticks(), *ax.yaxis.get_major_ticks()]:
            tick.tick1line.set_visible(False)
            tick.tick2line.set_visible(False)
            tick.label1.set_visible(False)
            tick.label2.set_visible(False)

        im = ax.imshow(cell_colors, alpha=0.3)
        patches = [mpatches.Patch(color=(*int_to_color_hash(cell_type.value), 0.3), label=str(cell_type))
                   for cell_type in CellType]
        plt.legend(handles=patches, bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

        annot = ax.annotate('', xy=(0, 0), xytext=(20, 20), textcoords='offset points',
                            bbox=dict(boxstyle='round', fc='w'),
                            arrowprops=dict(arrowstyle='->'))
        annot.set_visible(False)

        def _update_annot(event, terrain):
            annot.xy = (event.xdata, event.ydata)
            pos = terrain.make_lattice(Vec2(event.xdata, event.ydata))
            annot.set_text(terrain.cell_at(pos).annot())
            annot.get_bbox_patch().set_alpha(0.4)
            annot.set_visible(True)

        def _hover(event, terrain):
            vis = annot.get_visible()
            if event.inaxes == ax:
                cont, ind = im.contains(event)
                if cont:
                    _update_annot(event, terrain)
                    fig.canvas.draw_idle()
                else:
                    if vis:
                        annot.set_visible(False)
                        fig.canvas.draw_idle()

        fig = plt.gcf()
        fig.canvas.mpl_connect("motion_notify_event", lambda e: _hover(e, self))

        plt.xlim(-0.5, self.width - 0.5)
        plt.ylim(-0.5, self.height - 0.5)
        plt.subplots_adjust(right=0.8)

    def __repr__(self):
        res = ''
        for y in range(self.height):
            for x in range(self.width):
                res += str(self.grid[y][x])
                # res += '{'
                # res += f'ele: {self.elevations[y][x]}'
                # res += str(self.grid[y][x])
                # res += '} '
            res += '\n'
        return res
