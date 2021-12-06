from string import ascii_uppercase

from dataclasses import dataclass
from kivy.event import EventDispatcher
from kivy.properties import StringProperty, ListProperty


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
    def __init__(self):
        self.row = None
        self.col = None
        self.shot = False

    @property
    def pos(self):
        return self.row, self.col

    @pos.setter
    def pos(self, value):
        self.row, self.col = value


class Animal:

    def __init__(self):
        self.orientation = "NORTH"


class Snake:

    def __init__(self):
        self.img = "data/snake.jpeg"

class Board:

    def __init__(self):
        self.grid = self.init_grid()
        self.animals = []

    @staticmethod
    def init_grid():
        grid = {}
        for i in range(1, 11):
            for letter in ascii_uppercase[:10]:
                grid[(i, letter)] = []
        return grid



class Game:
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.status = "SETUP"
        self.board = Board()

