import json
import math
import random
import time
from datetime import datetime
from platform import system

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from pynput import keyboard

from .config import Config
from .enums import Personality, Gender, CellType, Neighborhood, State
from .terrain import Terrain
from .models import Cat
from .math import Vec2
from .utils import (
    char_to_cell_type,
    random_cell_type_list,
    max_health,
    get_sleep_probability,
    calc_force,
)
from .logging import Logger


class Simulation:
    """
    Members:
        Input parameters (included in `args`):
            n_steps

        Simulation states i.e. should be serialized:
            width
            height
            seed
            update
            population
            terrain
            temperature
            hour_of_day
    """

    def __init__(self, args):
        self.args = args

        # Initialize later
        self.seed = None
        self.n_steps = None
        self.population = None
        self.hour_of_day = None
        self.neighborhood = None
        self.neighborhood_radius = None
        self.continuous_food = None
        self.step = 0
        self.width = 0
        self.height = 0
        self.terrain = None
        self.elevations = None
        self.cell_types = None
        self.current_population = None
        self.results_file_path = None

        self._cats = []  # For internal tracking

        self.log_forces = True
        self.start_time = None

        self.key_listener = keyboard.Listener(on_press=lambda key: self._on_key_press(key, self))
        self.key_listener.start()

        self.save_file = f'states/simulation-state-{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.json'

        self.render_enabled = True
        self.render_pause_interval = 0.1
        self.render_pause = False
        self.plots = dict()  # render plots
        self.axs = []
        self.fig = None
        self.ani = None  # Animation

    @staticmethod
    def _on_key_press(key, simulation):
        if str(key) == "'p'":
            simulation.render_pause = not simulation.render_pause
        # Pause is done in render step to render text before going pause
        if simulation.ani is not None:
            simulation.ani.event_source.start()  # Unpause

    def _setup_from_file(self):
        pass

    def _setup_from_parameters(self):
        self.seed = self.args.seed
        self.n_steps = self.args.n_steps
        self.population = self.args.population
        self.hour_of_day = self.args.hour_of_day % 24
        self.neighborhood = Neighborhood.Moore if self.args.neighborhood == 'moore' else Neighborhood.VonNeumann
        self.neighborhood_radius = self.args.neighborhood_radius
        self.continuous_food = self.args.continuous_food
        self.results_file_path = self.args.results_file_path

        self.current_population = self.population
        self.step = 0

        random.seed(self.seed)

        # Build elevations
        dimensions_set = False
        if self.args.t_elevations_file is not None:
            with open(self.args.t_elevations_file, 'r') as ele_f:
                self.elevations = []
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
                    self.elevations.append(row)
                if len(self.elevations) == 0:
                    raise ValueError('Invalid elevation map.')

            self.height = len(self.elevations)
            self.width = width
            dimensions_set = True

        if self.args.t_cell_types_file is not None:
            with open(self.args.t_cell_types_file, 'r') as cell_f:
                self.cell_types = []
                width = -1
                for line in cell_f:
                    line = line.strip()
                    row = list(map(char_to_cell_type, line.split(' ')))
                    if width == -1:
                        width = len(row)
                        if width == 0:
                            raise ValueError('Invalid cell type map.')
                    elif width != len(row):
                        raise ValueError('Invalid cell type map.')
                    self.cell_types.append(row)
                if len(self.cell_types) == 0:
                    raise ValueError('Invalid cell type map.')

            if dimensions_set:
                if self.height != len(self.cell_types) or self.width != width:
                    raise ValueError('Elevation map and cell type map dimensions mismatch.')
            else:
                self.height = len(self.cell_types)
                self.width = width
                dimensions_set = True

        if not dimensions_set:
            self.height = self.args.t_height
            self.width = self.args.t_width

        if self.elevations is None:
            self.elevations = [[0 for _1 in range(self.width)] for _2 in range(self.height)]
        if self.cell_types is None:
            self.cell_types = [random_cell_type_list(self.width) for _ in range(self.height)]

        # Build terrain
        self.terrain = Terrain(width=self.width, height=self.height, elevations=self.elevations,
                               cell_types=self.cell_types)

        # Put cats on the terrain
        for i in range(self.population):
            x = random.randrange(0, self.terrain.width)
            y = random.randrange(0, self.terrain.height)
            personality = Personality.random()
            gender = Gender.random()
            age = random.randrange(0, 10)  # years
            health = max_health(age)
            cat = Cat(
                position=Vec2(x, y),
                age=age,
                personality=personality,
                gender=gender,
                health=health,
                state=State.active
            )
            self.terrain.put_cat(cat=cat)
            self._cats.append(cat)

    def _setup(self):
        Logger.log('Setting up simulation')
        t = time.time()
        self.start_time = t
        if self.args.state_file is not None:
            self._setup_from_file()
        else:
            self._setup_from_parameters()
        self._render_init()
        Logger.log(f'Elapsed {time.time() - t} s')

    def temperature(self):
        return 25 - 5 * math.cos(math.pi * self.hour_of_day / 12)

    def annot(self):
        s = ''
        s += f'Step: {self.step}/{self.n_steps}\n'
        s += f'Population: {self.current_population}'
        return s

    def serialize(self):
        return dict(
            seed=self.seed,
            n_steps=self.n_steps,
            population=self.population,
            hour_of_day=self.hour_of_day,
            neighborhood=str(self.neighborhood),
            neighborhood_radius=self.neighborhood_radius,
            continuous_food=self.continuous_food,
            step=self.step,
            width=self.width,
            height=self.height,
            current_population=self.current_population,
            cat_next_id=Cat.next_id(),
            elevations=self.elevations,
            cell_types=[[str(ct) for ct in row] for row in self.cell_types],
            terrain=self.terrain.serialize(),
            cats=[cat.serialize() for cat in self._cats],
        )

    def save_state(self):
        data = self.serialize()
        with open(self.save_file, 'w') as sf:
            json.dump(data, sf, indent=2)

    def _pre_update(self, cat, next_cats: list):
        cat.start_step()
        # -- Do actions --
        # Sleep if necessary
        if not cat.is_sleeping():
            sleep_probability = get_sleep_probability(self.terrain.cell_at(cat.position).cell_type, cat.health)
            if random.uniform(0, 1) < sleep_probability:
                cat.sleep()

        # Force wake up if health is low
        if cat.is_sleeping() and cat.health < Config.force_wake_up_health:
            Logger.log(f'[Alert] {cat} is forced to wake-up!')
            cat.wake_up()

        # Wake up if sleep duration is exceeded
        if cat.sleep_duration >= Config.sleep_time:
            cat.wake_up()

        cell = self.terrain.cell_at(cat.position)

        # Consume food
        if cell.cell_type == CellType.food and not cat.is_sleeping():
            consume_ammount = min(cell.food_amount, 10, cat.max_health() - cat.health)
            if consume_ammount > 0:
                cell.get_consumed(consume_ammount)
                cat.consume_food(consume_ammount)

        # Deliver off-spring
        if cat.is_pregnant() and cat.hours_since_last_conception >= Config.hours_to_deliver_offspring:
            cat_baby = cat.deliver()
            next_cats.append(cat_baby)
            self._cats.append(cat_baby)

    def _update(self, cat):
        cell = self.terrain.cell_at(cat.position)

        # Interact
        for other_cat in cell.cats:
            if cat.cat_id == other_cat.cat_id:
                continue
            cat.interact(other_cat, self.temperature())

        # -- Calculate forces --
        force = Vec2(0, 0)
        food_radius = self.neighborhood_radius
        if cat.health < 10:
            food_radius = 3 * self.neighborhood_radius
        elif cat.health < 25:
            food_radius = 1.5 * self.neighborhood_radius
        neighbors = self.terrain.neighbors(center=cat.position, r=food_radius,
                                           neighborhood=self.neighborhood)
        for other_cell in neighbors:
            # Food attraction
            if other_cell.cell_type == CellType.food:
                food_attraction = (other_cell.food_amount / 100) * cat.food_attraction()
                food_force = calc_force(food_attraction, cat.position, other_cell.position)
                force += food_force
                if self.log_forces:
                    Logger.log(f'[Force][Food] A force {food_force} is exerted on {cat}')

        neighbors = self.terrain.neighbors(center=cat.position, r=self.neighborhood_radius,
                                           neighborhood=self.neighborhood)
        for other_cell in neighbors:
            # Bed attraction
            if other_cell.cell_type == CellType.bed:
                bed_attraction = cat.bed_attraction()
                bed_force = calc_force(bed_attraction, cat.position, other_cell.position)
                force += bed_force
                if self.log_forces:
                    Logger.log(f'[Force][Bed] A force {bed_force} is exerted on {cat}')

            # Box attraction
            if other_cell.cell_type == CellType.box:
                box_attraction = cat.box_attraction()
                box_force = calc_force(box_attraction, cat.position, other_cell.position)
                force += box_force
                if self.log_forces:
                    Logger.log(f'[Force][Box] A force {box_force} is exerted on {cat}')

            # Mutual attraction
            for other_cat in other_cell.cats:
                if other_cat.cat_id == cat.cat_id:
                    continue
                mutual_attraction = cat.mutual_attraction(other_cat, self.temperature())
                mututal_force = calc_force(mutual_attraction, cat.position, other_cell.position)
                force += mututal_force
                if self.log_forces:
                    Logger.log(f'[Force][Mutual] A force {mututal_force} is exerted on {cat} by {other_cat}')

            # Trace attraction
            if other_cell.x_trace > 0 or other_cell.y_trace > 0:
                trace_attraction = cat.trace_attraction(other_cell.x_trace, other_cell.y_trace)
                trace_force = calc_force(trace_attraction, cat.position, other_cell.position)
                force += trace_force
                if self.log_forces:
                    Logger.log(
                        f'[Force][Trace] A force {trace_force} is exerted on {cat} by cell at {other_cell.position} '
                        f'x_trace={other_cell.x_trace} y_trace={other_cell.y_trace}')

            # Randomness
            random_force = cat.random_force()
            force += random_force
            if self.log_forces:
                Logger.log(f'[Force][Random] A force {random_force} is exerted on {cat} randomly')

        cat.add_force(force)
        if self.log_forces:
            Logger.log(f'[Force] Total force of {cat.get_force()} is exerted on {cat}')

    def _post_update(self, cat, next_cats):
        # Calculate movement with calculated force and elevation
        Logger.log(f'From position {cat.position} Target position {cat.position + cat.get_force()}')
        target_position = self.terrain.clamp(cat.position, cat.position + cat.get_force())
        Logger.log(f'Target position {target_position}')
        if cat.position != target_position:
            health_damage = self.terrain.health_damange_to_travel(cat.position, target_position)
            cat.move(target_position, health_damage)

        cat.finalize_step()

        if not cat.should_die():
            next_cats.append(cat)
        else:
            cat.die()

    def update(self):
        step = self.step + 1
        Logger.sep()
        Logger.log(f'Starting step: {step}')
        Logger.log(f'Day: {step // 24} Hour: {step % 24}')
        Logger.log(f'Hour of day: {self.hour_of_day + 1}')
        t = time.time()
        print(f'Step {step}')

        # Next states
        next_terrain = Terrain(width=self.width, height=self.height, elevations=self.elevations,
                               cell_types=self.cell_types, previous_terrain=self.terrain)
        next_cats = []

        # Refill food
        for y in range(self.height):
            for x in range(self.width):
                cell = self.terrain.at(x, y)
                if cell.cell_type == CellType.food:
                    if self.continuous_food:
                        cell.food_amount = Config.continuous_food_amount
                    elif self.hour_of_day == 12:
                        cell.food_amount = Config.new_food_amount

        for y in range(self.height):
            for x in range(self.width):
                for cat in self.terrain.cats_at(Vec2(x, y)):
                    self._pre_update(cat, next_cats)

        for y in range(self.height):
            for x in range(self.width):
                for cat in self.terrain.cats_at(Vec2(x, y)):
                    self._update(cat)

        for y in range(self.height):
            for x in range(self.width):
                for cat in self.terrain.cats_at(Vec2(x, y)):
                    self._post_update(cat, next_cats)

        for cat in self._cats:
            cat.update_state_hours()

        # Put new cats to the next terrain
        for next_cat in next_cats:
            next_terrain.put_cat(next_cat)
        self.current_population = len(next_cats)

        # Replace
        self.terrain = next_terrain

        # print('------------------')
        # print(self.terrain.console_render())
        # for row in self.terrain.grid:
        #     for cell in row:
        #         print(cell_type_to_char(cell.cell_type), end=' ')
        #     print()

        Logger.log(f'Finished step: {self.step}')
        Logger.log(f'Elapsed {time.time() - t} s')

        self.step += 1
        self.hour_of_day = (self.hour_of_day + 1) % 24

        self.save_state()

    def _render_init(self):
        if not self.render_enabled:
            return
        self.terrain.render_init(self.plots, self.axs, self.fig)
        self.plots['stat'] = self.fig.text(0.5, 0.1, '', ha="center")
        self.plots['bottom'] = self.fig.text(0.5, 0.01, '', ha="center")

    def _render(self, _step):
        if not self.render_enabled:
            return None,

        title_text = 'Cat Simulation'
        bottom_text = 'Press P to pause'
        if self.step == self.n_steps:
            title_text += ' (Completed)'
        if self.render_pause:
            title_text += ' (Paused)'
            bottom_text = 'Press P again to resume'
        self.fig.suptitle(title_text)
        self.plots['stat'].set_text(self.annot())
        self.plots['bottom'].set_text(bottom_text)

        if self.render_pause:
            self.ani.event_source.stop()  # pause

        self.terrain.render(self.plots, self.axs, self.fig)
        return self.plots.values()

    def _loop(self):
        self._setup()
        while not self.is_finished():
            self.update()
            yield self.step,
        self._finalize()

    @staticmethod
    def _show_window():
        # Show maximized window
        backend = plt.get_backend()
        cfm = plt.get_current_fig_manager()
        if backend == "wxAgg":
            cfm.frame.Maximize(True)
        elif backend == "TkAgg":
            if system() == "Windows":
                cfm.window.state("zoomed")  # This is windows only
            else:
                cfm.resize(*cfm.window.maxsize())
        elif backend == "QT4Agg":
            cfm.window.showMaximized()
        elif callable(getattr(cfm, "full_screen_toggle", None)):
            if not getattr(cfm, "flag_is_max", None):
                cfm.full_screen_toggle()
                cfm.flag_is_max = True
        else:
            raise RuntimeError("plt_maximize() is not implemented for current backend:", backend)
        plt.show()

    def start(self):
        if self.render_enabled:
            plt.rcParams['font.family'] = 'monospace'
            self.fig, self.axs = plt.subplots(1, 3)
            self.ani = animation.FuncAnimation(
                plt.gcf(),
                self._render,
                self._loop,
                save_count=1,
                init_func=lambda: None,
                interval=self.render_pause_interval * 1000,
                repeat=False,
            )
            self._show_window()
        else:
            for _step in self._loop():
                continue

    def is_finished(self):
        return self.step >= self.n_steps or self.population <= 0

    def _finalize(self):
        Logger.sep()
        Logger.log('Simulation is finishing')

        if not self.continuous_food:
            for y in range(self.height):
                for x in range(self.width):
                    cell = self.terrain.at(x, y)
                    if cell.cell_type == CellType.food:
                        Logger.log(f'Cell at {cell.position} has {cell.food_amount} food remaining')

        self._cats.sort(key=lambda c: c.cat_id)
        alive = sum([cat.is_alive() for cat in self._cats])
        Logger.log(f'{alive} cats alive')

        for cat in self._cats:
            Logger.log(f'{cat}')
            Logger.log(cat.summary)
            # state_hours = {str(state): hours for state, hours in cat.state_hours.items()}
            # Logger.log(f'This cat spent time doing {state_hours}')
            # Logger.log(f'This cat moved total distance of {cat.total_distance_moved:.2f} units')

        with open(self.results_file_path, 'w') as rf:
            data = self.serialize()
            json.dump(data, rf, indent=4)

        Logger.log('Simulation is finished')
        Logger.log(f'Elapsed {time.time() - self.start_time} s')
