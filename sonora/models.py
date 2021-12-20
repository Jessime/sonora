from enum import Enum
from dataclasses import dataclass
from kivy.event import EventDispatcher
from kivy.properties import StringProperty, ListProperty, ObjectProperty, NumericProperty
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
    img = None

    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.shot = False

    def __repr__(self):
        temp = f"{self.img=}"
        return f"[{self.__class__.__name__}: {self.shot=} {temp}]"

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

    def __init__(self, row, col):
        super(SnakeHead, self).__init__(row, col)


class SnakeBody(Segment):
    img = "/Users/jessime.kirk/Code/me/sonora2/sonora/data/snake_body.jpeg"

    def __init__(self, row, col):
        super(SnakeBody, self).__init__(row, col)


class SnakeTail(Segment):
    img = "/Users/jessime.kirk/Code/me/sonora2/sonora/data/snake_tail.jpeg"

    def __init__(self, row, col):
        super(SnakeTail, self).__init__(row, col)


class Snake(Animal):
    img = "/Users/jessime.kirk/Code/me/sonora2/sonora/data/snake.jpeg"
    cls_segments = {
        (0, 0): SnakeTail,
        (-1, 0): SnakeBody,
        (-2, 0): SnakeHead,
    }

    def __init__(self, base_row, base_col):
        super(Snake, self).__init__(base_row, base_col)


class CentipedeHead(Segment):
    img = "/Users/jessime.kirk/Code/me/sonora2/sonora/data/centipede_head.png"


class CentipedeBody(Segment):
    img = "/Users/jessime.kirk/Code/me/sonora2/sonora/data/centipede_body.png"


class CentipedeTail(Segment):
    img = "/Users/jessime.kirk/Code/me/sonora2/sonora/data/centipede_tail.png"


class Centipede(Animal):
    img = "/Users/jessime.kirk/Code/me/sonora2/sonora/data/centipede.png"
    cls_segments = {
        (0, 0): CentipedeTail,
        (0, 1): CentipedeBody,
        (0, 2): CentipedeHead,
    }

    def __init__(self, base_row, base_col):
        super(Centipede, self).__init__(base_row, base_col)


class JavelinaMouth(Segment):
    img = "/Users/jessime.kirk/Code/me/sonora2/sonora/data/centipede_mouth.png"


class JavelinaHead(Segment):
    img = "/Users/jessime.kirk/Code/me/sonora2/sonora/data/javelina_head.jpeg"


class JavelinaBack(Segment):
    img = "/Users/jessime.kirk/Code/me/sonora2/sonora/data/javelina_back.png"


class JavelinaBottom(Segment):
    img = "/Users/jessime.kirk/Code/me/sonora2/sonora/data/javelina_bottom.png"


class Javelina(Animal):
    img = "/Users/jessime.kirk/Code/me/sonora2/sonora/data/javelina.jpeg"
    cls_segments = {
        (0, 0): JavelinaMouth,
        (0, 1): JavelinaBottom,
        (-1, 0): JavelinaHead,
        (-1, 1): JavelinaBack,
    }

    def __init__(self, base_row, base_col):
        super(Javelina, self).__init__(base_row, base_col)


class RingtailHead(Segment):
    img = "/Users/jessime.kirk/Code/me/sonora2/sonora/data/ringtail_head.jpeg"


class RingtailBody(Segment):
    img = "/Users/jessime.kirk/Code/me/sonora2/sonora/data/ringtail_body.jpeg"


class RingtailTail(Segment):
    img = "/Users/jessime.kirk/Code/me/sonora2/sonora/data/ringtail_tail.jpeg"


class RingtailTail2(Segment):
    img = "/Users/jessime.kirk/Code/me/sonora2/sonora/data/ringtail_tail2.jpeg"


class Ringtail(Animal):
    img = "/Users/jessime.kirk/Code/me/sonora2/sonora/data/javelina.jpeg"
    cls_segments = {
        (0, 0): RingtailHead,
        (0, 1): RingtailBody,
        (0, 2): RingtailTail,
        (1, 2): RingtailTail2,
    }

    def __init__(self, base_row, base_col):
        super(Ringtail, self).__init__(base_row, base_col)


class AnimalTypes(Enum):
    SNAKE = Snake
    CENTIPEDE = Centipede
    JAVELINA = Javelina
    RINGTAIL = Ringtail


class Square(EventDispatcher):
    """A single tile on the Board.

    A Square can only contain one object at a time.
    This is mostly for simplicity.
    1. It's how Battleship does it.
    2. There's no good way to represent multiple objects on a square at the same time.
    """
    obj = ObjectProperty(allownone=True)

    def __repr__(self):
        return "" if self.obj is None else str(self.obj)


class Board:

    def __init__(self):
        self.grid = self.init_grid()
        self.animals = []

    @staticmethod
    def init_grid():
        grid = {}
        for i in range(1, 11):
            for letter in COLS:
                grid[(i, letter)] = Square()
        return grid


# @dataclass
class GameSetup(EventDispatcher):
    selected_animal_type = ObjectProperty(None, allownone=True)
    active_page = NumericProperty()
    pages: tuple[tuple[AnimalTypes]] = (
        (AnimalTypes.SNAKE, AnimalTypes.CENTIPEDE),
        (AnimalTypes.JAVELINA, AnimalTypes.RINGTAIL)
    )  # TODO add other tuples
    board: Board = Board()

    @property
    def avail_types(self):
        page = self.pages[self.active_page]
        return page[0].value, page[1].value


class Game:
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.status = "SETUP"
        self.board = Board()  # TODO Do I want to make this here or pass it from the setup? :shrug:

