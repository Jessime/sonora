from enum import Enum
from dataclasses import dataclass
from kivy.event import EventDispatcher
from kivy.properties import StringProperty, ListProperty, ObjectProperty
from typing import Optional

from sonora.static import COLS

# @dataclass
class User(EventDispatcher):
    """Info about the individual playing on this instance of the app."""
    username = StringProperty("")
    game_rows = ListProperty([])  # These are <LiveObject: anvil.tables.Row>

    def on_username(self, a, b):
        print(type(a), a)
        print(type(b), b)
        return self.username


class Segment:
    """A single square of an Animal"""

    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.shot = False

    @property
    def loc(self):
        return self.row, self.col

    @loc.setter
    def loc(self, value):
        self.row, self.col = value


class Animal:
    img = None
    cls_segments = {}

    def __init__(self, base_row, base_col):
        self.base_row = base_row
        self.base_col = base_col

        self.segments = self.make_segments()

    def make_segments(self):
        """Find the final locations of all the segment for an animal.

        The locations for each seg of an animal are originally specified relative to the top-left of the animals.
        It isn't until a tile on the board is chosen that all of the absolute locations can be calculated.
        """
        segments = []
        for (rel_row, rel_col), seg_cls in self.cls_segments.items():
            abs_row = self.base_row + rel_row
            abs_col = COLS[COLS.find(self.base_col) + rel_col]
            seg = seg_cls(abs_row, abs_col)
            segments.append(seg)
        return segments


class SnakeHead(Segment):
    img = "/Users/jessime.kirk/Code/me/sonora2/sonora/data/snake_head.jpeg"


class SnakeBody(Segment):
    img = "/Users/jessime.kirk/Code/me/sonora2/sonora/data/snake_body.jpeg"


class SnakeTail(Segment):
    img = "/Users/jessime.kirk/Code/me/sonora2/sonora/data/snake_tail.jpeg"


class Snake(Animal):
    img = "/Users/jessime.kirk/Code/me/sonora2/sonora/data/snake.jpeg"
    cls_segments = {
        (0, 0): SnakeHead,
        (-1, 0): SnakeBody,
        (-2, 0): SnakeTail,
    }

    def __init__(self, base_row, base_col):
        super(Snake, self).__init__(base_row, base_col)


class CentipedeHead(Segment):
    img = "/Users/jessime.kirk/Code/me/sonora2/sonora/data/snake_head.jpeg"


class CentipedeBody(Segment):
    img = "/Users/jessime.kirk/Code/me/sonora2/sonora/data/snake_body.jpeg"


class CentipedeTail(Segment):
    img = "/Users/jessime.kirk/Code/me/sonora2/sonora/data/snake_tail.jpeg"


class Centipede(Animal):
    img = "/Users/jessime.kirk/Code/me/sonora2/sonora/data/centipede.png"
    cls_segments = {
        (0, 0): CentipedeTail,
        (0, 1): CentipedeBody,
        (0, 2): CentipedeHead,
    }

    def __init__(self, base_row, base_col):
        super(Centipede, self).__init__(base_row, base_col)


class AnimalTypes(Enum):
    SNAKE = Snake
    CENTIPEDE = Centipede


class Board:

    def __init__(self):
        self.grid = self.init_grid()
        self.animals = []

    @staticmethod
    def init_grid():
        grid = {}
        for i in range(1, 11):
            for letter in COLS:
                grid[(i, letter)] = []
        return grid


# @dataclass
class GameSetup(EventDispatcher):
    selected_animal_type = ObjectProperty(None, allownone=True)
    pages: tuple[tuple[AnimalTypes]] = ((AnimalTypes.SNAKE, AnimalTypes.CENTIPEDE),)  # TODO add other tuples
    active_page: int = 0
    board: Board = Board()


class Game:
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.status = "SETUP"
        self.board = Board()  # TODO Do I want to make this here or pass it from the setup? :shrug:

