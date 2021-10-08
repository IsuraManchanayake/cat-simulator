from math import log  # Python math module
import random

from .config import Config
from .enums import Gender, Personality, State
from .math import Vec2  # Project math module
from .utils import max_health
from .logging import Logger


class Cat:
    _count = 0

    def __init__(self, position: Vec2, age: float, gender: Gender, personality: Personality, health: int, state: State,
                 sleep_duration=0, fetus=None, hours_since_last_conception=None, cat_id=None):
        """
        Age is in years.
        """
        self.cat_id = Cat._count if cat_id is None else cat_id
        self.position = position
        self.age = age
        self.gender = gender
        self.personality = personality
        self.health = health
        self.state = state
        self.hours_since_last_conception = hours_since_last_conception
        self.sleep_duration = sleep_duration
        self.fetus = fetus

        Cat._count += 1
        self._force = Vec2(0, 0)
        self._health = self.health
        self._step_finalized = True

        Logger.log(f'[Create] Cat is created {self}')

    def mutual_attraction(self, other_cat: 'Cat', temperature: float):
        """
        Returns attraction level in the range -1, 1.
        Temperature is in celcius.
        When temperature is high, sexual drive is high
        """
        if self.is_sleeping():
            return 0
        if self.gender != other_cat.gender:
            if self.is_sexually_active() and other_cat.is_sexually_active():
                return 0.9 if temperature > 28 else 0.7
            else:
                return 0.75 * self._mutual_attraction_factor(other_cat)
        else:
            return self._mutual_attraction_factor(other_cat)

    def _mutual_attraction_factor(self, other_cat: 'Cat'):
        """
        Repulsive when `other_cat` is older.
        Attractive when `other_cat` is younger for dominance.
        If both cats have friendly personalities, the attraction is always mutual.
        """
        if self.personality == other_cat.personality:
            return 0.7
        return self._dominance_factor(other_cat)

    def _dominance_factor(self, other_cat: 'Cat'):
        return self._strength() - other_cat._strength()
        # d = self.health - other_cat.health  # health difference
        # factor = (1 - 0.6 ** d) / (1 + 0.6 ** d) * abs(self.age - other_cat.age) / 20
        # return factor

    def _strength(self):
        return self.health / 100

    def food_attraction(self):
        """
        Infinite amount of drive to food when health is close to 0.
        No attraction to food when health is 100.
        """
        if self.is_sleeping():
            return 0
        return -log(self.health / self.max_health())

    def bed_attraction(self):
        if self.is_sleeping():
            return 0
        if self.age < 2 / 12:
            return 0.5
        else:
            if self.health > 95:
                return 0.5
            else:
                return 0.1

    def box_attraction(self):
        return self.bed_attraction()

    def trace_attraction(self, x_trace, y_trace):
        if self.is_sleeping():
            return 0
        same_personality_trace = x_trace if self.personality == Personality.X else y_trace
        opposite_personality_trace = y_trace if self.personality == Personality.X else x_trace
        effective_trace = same_personality_trace - opposite_personality_trace
        return effective_trace * Config.trace_attraction_factor

    def move(self, target_position, health_damage):
        Logger.log(f'[Action] {self} is moving to {target_position}')
        self.position = target_position
        self.damage_health(health_damage)

    def interact(self, other_cat: 'Cat', temperature: float):
        """
        Interaction between two cats when they are in the same cell.
        """
        if self.cat_id == other_cat.cat_id:
            return
        if self.is_sleeping():
            return
        if other_cat.is_sleeping():
            return
        if self.gender != other_cat.gender:
            if self.is_sexually_active() and other_cat.is_sexually_active():
                reproduction_probability = 0.9 if temperature > 28 else 0.7
                if random.uniform(0, 1) < reproduction_probability:
                    female_cat, male_cat = Cat.choose_female_cat(self, other_cat)
                    female_cat.conceive(male_cat)
                    return
        if self.personality != other_cat.personality:
            dominance = self._dominance_factor(other_cat)
            attacking_probability = min(0.0, dominance)
            if random.uniform(0, 1) < attacking_probability:
                power = dominance * 10
                self.attack(other_cat, power)
                return

    @staticmethod
    def choose_female_cat(cat_1, cat_2):
        return (cat_1, cat_2) if cat_1.gender == Gender.female else (cat_2, cat_1)

    def is_sexually_active(self):
        return self.age > 4 / 12 and not self.is_pregnant()  # 4 months

    def attack(self, other_cat, power):
        Logger.log(f'[Action] {self} is attacking {other_cat} with {power} power')
        other_cat.damage_health(power)
        self.damage_health(power / 5)  # Attacking drains energy

    def conceive(self, other_cat):
        Logger.log(f'[Action] {self} got conceived by {other_cat}')
        self.hours_since_last_conception = 0
        self.fetus = Cat(
            position=self.position,
            personality=random.choice([self.gender, other_cat.personality]),
            age=0,
            gender=Gender.random(),
            health=max_health(0),
            state=State.sleeping,
        )

    def deliver(self):
        if self.fetus is None:
            return
        cat_baby = self.fetus
        self.fetus = None
        cat_baby.position = self.position
        cat_baby.state = State.active
        Logger.log(f'[Action] {self} delivered {cat_baby}')
        return cat_baby

    def consume_food(self, amount):
        Logger.log(f'[Action] {self} is consuming {amount} foods')
        self._health = min(self.max_health(), self._health + amount)

    def damage_health(self, amount):
        # if amount == 0:
        #     return
        Logger.log(f'[Alert] {self} got damaged {amount}')
        self._health = max(0, self._health - amount)

    def age_up(self, hours=1):
        self.age += hours/(365 * 24)
        self.damage_health(1)
        if self.state == State.sleeping:
            self.sleep_duration += hours
        if self.hours_since_last_conception is not None:
            self.hours_since_last_conception += hours

    def wake_up(self):
        Logger.log(f'[Action] {self} is wake-up after {self.sleep_duration} hours of sleep')
        self.state = State.active
        self.sleep_duration = 0

    def sleep(self):
        Logger.log(f'[Action] {self} is starting to sleep')
        self.state = State.sleeping
        self.sleep_duration = 0

    def add_force(self, force):
        self._force += force

    def get_force(self):
        return self._force

    def start_step(self):
        if self._step_finalized:
            self._step_finalized = False
        else:
            raise ValueError('Trying to start new step without finalizing the last step.')

    def finalize_step(self):
        self._force = Vec2(0, 0)
        self.health = self._health
        self.age_up()
        self._step_finalized = True

    def max_health(self):
        return max_health(self.age)

    def is_pregnant(self):
        return self.gender == Gender.female and self.fetus is not None

    def is_sleeping(self):
        return self.state == State.sleeping

    def is_dead(self):
        return self.health <= 0 or self.age >= Config.max_life_span

    def __hash__(self):
        return hash((self.cat_id,))

    def __eq__(self, other):
        return self.cat_id == other.cat_id

    def annot(self):
        s = ''
        s += f'    {{cat_id={self.cat_id}, position={self.position}\n'
        s += f'    age={self.age:.2f}, health={self.health:.2f}\n'
        s += f'    gender={self.gender}, personality={self.personality}\n'
        s += f'    state={self.state}, hslc={self.hours_since_last_conception}\n'
        s += f'    sleep_duration={self.sleep_duration}'
        if self.fetus is not None:
            s += f'    fetus={self.fetus.annot()}'
        s += '}'
        return s

    def __repr__(self):
        return f'Cat{{cat_id={self.cat_id}, position={self.position}, age={self.age:.4f}, health={self.health:.4f}, ' \
               f'gender={self.gender}, personality={self.personality}, state={self.state}}}'
        # return f'Cat{{cat_id={self.cat_id}, position={self.position}, age={self.age:.4f}, ' \
        #        f'health={self.health:.4f}, gender={self.gender}, personality={self.personality}, ' \
        #        f'state={self.state}, sleep_duration={self.sleep_duration}, ' \
        #        f'hours_since_last_conception={self.hours_since_last_conception}}} '
