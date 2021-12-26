import pickle
from enum import Enum
from gzip import compress, decompress

from anvil import BlobMedia
from kivy.event import EventDispatcher
from kivy.properties import BooleanProperty, ListProperty, NumericProperty, ObjectProperty, StringProperty
from loguru import logger
from more_itertools import only

from sonora.static import COLS, SetupStatus, SetupStatusInternal, Status


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

    def serialize(self):
        self_data = {
            "class": self.__class__.__name__,
            "params": {"row": self.row, "col": self.col},
            "attrs": {"shot": self.shot},
        }
        return self_data

    @classmethod
    def deserialize(cls, db_rep):
        new = cls(**db_rep["params"])
        for name, value in db_rep["attrs"].items():
            setattr(new, name, value)
        return new


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

    def serialize(self):
        self_data = {
            "class": self.__class__.__name__,
            "params": {
                "base_row": self.base_row,
                "base_col": self.base_col,
            },
            "attrs": {
                "segments": [seg.serialize() for seg in self.segments],
            },
        }
        return self_data

    @classmethod
    def deserialize(cls, db_rep):
        new = cls(**db_rep["params"])
        segments = []
        for seg_data in db_rep["attrs"]["segments"]:
            new_seg = globals()[seg_data["class"]].deserialize(seg_data)
            segments.append(new_seg)
        setattr(new, "segments", segments)
        return new


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
    img = "/Users/jessime.kirk/Code/me/sonora2/sonora/data/javelina_mouth.jpeg"


class JavelinaHead(Segment):
    img = "/Users/jessime.kirk/Code/me/sonora2/sonora/data/javelina_head.jpeg"


class JavelinaBack(Segment):
    img = "/Users/jessime.kirk/Code/me/sonora2/sonora/data/javelina_back.jpeg"


class JavelinaBottom(Segment):
    img = "/Users/jessime.kirk/Code/me/sonora2/sonora/data/javelina_bottom.jpeg"


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
    img = "/Users/jessime.kirk/Code/me/sonora2/sonora/data/ringtail.png"
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

    @classmethod
    def deserialize(cls, db_rep):

        pkl = pickle.loads(decompress(db_rep.get_bytes()))
        if pkl is None:
            return cls()  # TODO this might be buggy :shrug:
        new = cls()
        animals = [globals()[animal["class"]].deserialize(animal) for animal in pkl]
        setattr(new, "animals", animals)

        for animal in animals:
            for seg in animal.segments:
                new.grid[(seg.row, seg.col)].obj = seg
        return new

    def serialize(self):
        """Represent the board in a json serializable format

        Importantly, `grid` and `animals` are mostly duplicate data.
        Serializing the animals is enough to reconstruct everything later.
        """
        simple_board = [animal.serialize() for animal in self.animals]
        return simple_board


class GameSetup(EventDispatcher):
    selected_animal_type = ObjectProperty(None, allownone=True)
    active_page = NumericProperty()
    is_first_player = BooleanProperty(False)
    pages: tuple[tuple[AnimalTypes]] = (
        (AnimalTypes.SNAKE, AnimalTypes.CENTIPEDE),
        (AnimalTypes.JAVELINA, AnimalTypes.RINGTAIL),
    )  # TODO add other tuples
    board: Board = Board()

    @property
    def avail_types(self):
        page = self.pages[self.active_page]
        return page[0].value, page[1].value

    def clear_board_of_active_page(self):
        avail_types = self.avail_types
        existing = only((a for a in self.board.animals if isinstance(a, avail_types)))
        if existing is None:
            logger.info(f"There's no animal on the board yet.")
        else:
            logger.info(f"Removing {existing} from board.")
            for seg in existing.segments:
                self.board.grid[(seg.row, seg.col)].obj = None
            self.board.animals.remove(existing)


class Game:
    """Translation layer between the DB representation and the players.

    Most importantly, there's only one game representation.
    But, each player wants to view the game as "theirs".
    And the other player should be the "opponent".

    It would be inefficient to store two copies of this data.
    (And maybe equally confusing).
    This class allows each player to have their own view of the game,
    while running off of the same database data.
    ---


    """

    _instance_count = 0

    def __init__(self, db_rep=None, user=None):
        Game._instance_count += 1
        if db_rep is None or user is None:
            if Game._instance_count == 1:
                logger.info("Created first (and only temporarily empty) Game instance")
                return
            err_msg = "Only the initial/global instance is allowed to be unpopulated on instantiation."
            raise ValueError(err_msg)
        logger.info(f"Created game instance #{self._instance_count}")
        self.db_rep = db_rep

        self.you_are_p1 = db_rep["player1"]["username"] == user.username
        self.board_column = "player1_board" if self.you_are_p1 else "player2_board"
        self.opponent = (db_rep["player2"] if self.you_are_p1 else db_rep["player1"])["username"]
        self._board = Board.deserialize(db_rep[self.board_column])

    @property
    def setup_status(self):
        if self.db_rep["setup_status"] == SetupStatus.NEITHER.value:
            return SetupStatus.NEITHER
        if self.db_rep["setup_status"] == SetupStatus.COMPLETE.value:
            return SetupStatus.COMPLETE
        just_you_done = self.db_rep["setup_status"] == SetupStatusInternal.PLAYER1.value and self.you_are_p1
        if just_you_done:
            return SetupStatus.YOU_DONE_OPP_NOT
        return SetupStatus.OPP_DONE_YOU_NOT

    @setup_status.setter
    def setup_status(self, new):
        self.db_rep["setup_status"] = new.value

    @property
    def status(self):
        return Status[self.db_rep["status"]]

    @status.setter
    def status(self, new):
        pass

    @property
    def board(self):
        return self._board

    @board.setter
    def board(self, new):
        self._board = new
        self.commit_board()

    def commit_board(self):
        logger.info("Committing board:")
        simple_board = self._board.serialize()
        logger.info(str(simple_board))
        self.db_rep[self.board_column] = BlobMedia("text/plain", compress(pickle.dumps(simple_board)))

    def notify_of_setup_finished(self):
        if self.setup_status == SetupStatus.NEITHER and self.you_are_p1:
            self.setup_status = SetupStatusInternal.PLAYER1
        elif self.setup_status == SetupStatus.NEITHER and not self.you_are_p1:
            self.setup_status = SetupStatusInternal.PLAYER2
        else:
            self.setup_status = SetupStatus.COMPLETE
