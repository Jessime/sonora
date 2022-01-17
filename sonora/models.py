import pickle
from gzip import compress, decompress

from anvil import BlobMedia
from kivy.event import EventDispatcher
from kivy.properties import BooleanProperty, ListProperty, NumericProperty, ObjectProperty, StringProperty
from loguru import logger
from more_itertools import only

from sonora import board_objects
from sonora.board_objects import Animal, AnimalTypes, Miss, Photo, Square
from sonora.static import COLS, SetupStatus, SetupStatusInternal, Status


class User(EventDispatcher):
    """Info about the individual playing on this instance of the app."""

    username = StringProperty("")
    game_rows = ListProperty([])  # These are <LiveObject: anvil.tables.Row>

    def on_username(self, arg1, arg2):
        return self.username


class Board:
    def __init__(self):
        self.grid = self.init_grid()
        self.contents = []

        self.full_animal_just_shot = None  # Note that Game has same attribute, since it's an EventDispatcher

    def __add__(self, board_obj):
        if hasattr(board_obj, "segments"):
            for seg in board_obj.segments:
                self.grid[seg.loc].obj = seg
        else:
            self.grid[board_obj.loc].obj = board_obj
        self.contents.append(board_obj)
        logger.info(f"Added {board_obj} to board.")

    def __sub__(self, board_obj):
        if hasattr(board_obj, "segments"):
            for seg in board_obj.segments:
                self.grid[seg.loc].obj = None
        else:
            self.grid[board_obj.loc].obj = None
        self.contents.remove(board_obj)
        logger.info(f"Removed {board_obj} from board.")

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
            return cls()

        new = cls()

        def find_cls(board_obj):
            return getattr(board_objects, board_obj["class"])

        contents = [find_cls(board_obj).deserialize(board_obj) for board_obj in pkl]
        setattr(new, "contents", contents)

        for board_obj in contents:
            if hasattr(board_obj, "segments"):
                for seg in board_obj.segments:
                    new.grid[seg.loc].obj = seg
            else:
                new.grid[board_obj.loc].obj = board_obj
        return new

    def serialize(self):
        """Represent the board in a json serializable format

        Importantly, `grid` and `animals` are mostly duplicate data.
        Serializing the animals is enough to reconstruct everything later.
        """
        simple_board = [board_obj.serialize() for board_obj in self.contents]
        return simple_board

    def clear_of_types(self, types):
        """Remove the only instance of one or more types from the board."""
        existing = only((a for a in self.contents if isinstance(a, types)))
        if existing is None:
            logger.info(f"There are no {types} on the board yet.")
        else:
            self - existing

    def set_full_animal_shot(self, seg):
        """This gets triggered immediately after an animal is shot and will be consumed by the Game

        "Consumed" here means that `full_animal_just_shot` will quickly get set back to `None`.
        """
        animal = seg.animal_backref(self)
        if animal.shot:
            self.full_animal_just_shot = animal

    def photo_to_shot_or_miss(self):
        """A weird func that resolves a photo into a permanent shot-or-miss.

        The reason this function is weird is because I like two design choices:
        1. A Board Square can only contain one object at a time.
        2. A Photo is a normal board object that can utilize general board functionality.

        These two things means that Segments get removed from the board.grid when a photo is placed on it.
        This function will either:
        1. Turn the photo into a permanent Miss
        2. Replace the original segment to the grid and mark it as shot.
        """
        photo = only((a for a in self.contents if isinstance(a, Photo)))
        self - photo

        def try_find_match(contents):
            """brute force check if any segments were in the spot"""
            for board_obj in contents:
                if hasattr(board_obj, "segments"):
                    for seg in board_obj.segments:
                        if photo.loc == seg.loc:
                            return seg

        match = try_find_match(self.contents)
        if match is None:
            self + Miss(*photo.loc)
        else:
            match.shot = True
            self.grid[photo.loc].obj = match
            self.set_full_animal_shot(match)

    def perform_surgery(self, new_seg, og_seg):
        """Update an animal that was shot on opps turn.

        This name is intentionally dramatic because we have to do some hacks.
        I want to trigger an update of the image, which means I need a new object id.
        And I also want to object id to stay consistent inside the animal.
        """
        animal = og_seg.animal_backref(self)
        animal.segments = [new_seg if s.loc == new_seg.loc else s for s in animal.segments]
        self.grid[new_seg.loc].obj = new_seg


class GameSetup(EventDispatcher):

    selected_animal_type = ObjectProperty(None, allownone=True)
    active_page = NumericProperty()
    is_first_player = BooleanProperty(False)
    pages: tuple[tuple[AnimalTypes]] = (
        (AnimalTypes.FLYCATCHER, AnimalTypes.PYRRHULOXIA),
        (AnimalTypes.SNAKE, AnimalTypes.CENTIPEDE),
        (AnimalTypes.JACKRABBIT, AnimalTypes.GILA),
        (AnimalTypes.JAVELINA, AnimalTypes.RINGTAIL),
        (AnimalTypes.BIGHORN, AnimalTypes.BOBCAT),
    )  # TODO add other tuples
    board: Board = Board()

    @property
    def avail_types(self):
        page = self.pages[self.active_page]
        return page[0].value, page[1].value


class Game(EventDispatcher):
    _instance_count = 0
    db_rep = ObjectProperty()
    you_are_p1 = BooleanProperty(defaultvalue=None)
    your_board_col_label = StringProperty()
    opp_board_col_label = StringProperty()
    opponent = StringProperty()
    board = ObjectProperty()
    opp_board = ObjectProperty()
    setup_status = ObjectProperty()
    status = ObjectProperty()
    your_turn = BooleanProperty(defaultvalue=None)
    winner = StringProperty()
    full_animal_just_shot = ObjectProperty(defaultvalue=None, allownone=True)

    def __init__(self, db_rep=None, user=None, **kwargs):
        super(Game, self).__init__(**kwargs)
        Game._instance_count += 1
        if db_rep is None or user is None:
            if Game._instance_count == 1:
                logger.info("Created first (and only temporarily empty) Game instance")
                return
            err_msg = "Only the initial/global instance is allowed to be unpopulated on instantiation."
            raise ValueError(err_msg)
        self.db_rep = db_rep
        self.your_name = user.username
        self.you_are_p1 = db_rep["player1"]["username"] == user.username
        self.opponent = (db_rep["player2"] if self.you_are_p1 else db_rep["player1"])["username"]
        self.your_board_col_label = "player1_board" if self.you_are_p1 else "player2_board"
        self.opp_board_col_label = "player2_board" if self.you_are_p1 else "player1_board"
        self.board = Board.deserialize(db_rep[self.your_board_col_label])
        self.opp_board = Board.deserialize(db_rep[self.opp_board_col_label])
        self.setup_status = self.fetch_setup_status()
        self.status = Status[self.db_rep["status"]]
        self.your_turn = self.db_rep["turn"]["username"] == user.username

        self.bind(board=self.commit_board)
        self.bind(opp_board=self.commit_opp_board)
        self.bind(setup_status=self.commit_setup_status)
        self.bind(status=self.commit_status)

    def fetch_setup_status(self):
        if self.db_rep["setup_status"] == SetupStatus.NEITHER.value:
            return SetupStatus.NEITHER
        if self.db_rep["setup_status"] == SetupStatus.COMPLETE.value:
            return SetupStatus.COMPLETE
        just_you_done = (
            self.db_rep["setup_status"] == SetupStatusInternal.PLAYER1_DONE.value
            and self.you_are_p1
            or self.db_rep["setup_status"] == SetupStatusInternal.PLAYER2_DONE.value
            and not self.you_are_p1
        )
        if just_you_done:
            return SetupStatus.YOU_DONE_OPP_NOT
        return SetupStatus.OPP_DONE_YOU_NOT

    def _commit_either_board(self, board, col_label):
        """Private func to save board after which column to save to has been sorted out."""
        logger.info("Committing board:")
        simple_board = board.serialize()
        logger.info(str(simple_board))
        self.db_rep[col_label] = BlobMedia("text/plain", compress(pickle.dumps(simple_board)))

    def commit_board(self, _, board):
        self._commit_either_board(board, self.your_board_col_label)

    def commit_opp_board(self, _, opp_board):
        self._commit_either_board(opp_board, self.opp_board_col_label)

    def commit_status(self, _, status):
        self.db_rep["status"] = status.value

    def commit_winner(self):
        """This only gets called if you are the winner."""
        self.db_rep["winner"] = self.db_rep["player1"] if self.you_are_p1 else self.db_rep["player2"]

    def commit_setup_status(self, _, setup_status):
        if setup_status == SetupStatus.YOU_DONE_OPP_NOT and self.you_are_p1:
            self.db_rep["setup_status"] = SetupStatusInternal.PLAYER1_DONE.value
        elif setup_status == SetupStatus.YOU_DONE_OPP_NOT and not self.you_are_p1:
            self.db_rep["setup_status"] = SetupStatusInternal.PLAYER2_DONE.value
        elif setup_status == SetupStatus.COMPLETE:
            self.db_rep["setup_status"] = SetupStatus.COMPLETE.value
        else:
            ValueError(f"{setup_status} is not in a valid state at this time.")

    def switch_to_opps_turn(self):
        self.db_rep["turn"] = self.db_rep["player2"] if self.you_are_p1 else self.db_rep["player1"]
        self.your_turn = False

    def notify_of_setup_finished(self):
        fresh_setup_status = self.fetch_setup_status()  # in case your opp finished while you were messing around
        if fresh_setup_status == SetupStatus.NEITHER:
            self.setup_status = SetupStatus.YOU_DONE_OPP_NOT
        elif fresh_setup_status == SetupStatus.OPP_DONE_YOU_NOT:
            self.setup_status = SetupStatus.COMPLETE
        else:
            raise ValueError(f"{fresh_setup_status} is not a valid setup status.")

    def resolve_turn_updates(self, arg1, polled_opp_finish_turn):
        """Called when your opp finishes a turn.

        Note: it already been verified that they haven't won.
        At this point, the only thing left to do is to deserialize your new board.
        This takes a little bit of effort because we need to make sure the correct view is applied to your board.
        We hunt down what changed, and update that square.
        There are only two possibilities:

        1. A hit
        2. A miss
        """
        if not polled_opp_finish_turn:
            return
        new_board = Board.deserialize(self.db_rep[self.your_board_col_label])
        for obj in new_board.contents[::-1]:  # Most likely case is a miss
            if hasattr(obj, "segments"):
                for seg in obj.segments:
                    if not seg.shot:
                        continue
                    og_seg = self.board.grid[seg.loc].obj
                    if not og_seg.shot:
                        self.board.perform_surgery(seg, og_seg)
                        break
            else:
                is_new_obj = self.board.grid[obj.loc].obj is None
                if is_new_obj:
                    self.board + obj
                    break

    def resolve_full_animal_just_shot(self):
        """If the last segment in an animal is shot, we need to notify the board view to update other squares."""
        animal = self.opp_board.full_animal_just_shot
        if animal is not None:
            self.full_animal_just_shot = animal
            # Cleanup
            self.full_animal_just_shot = None
            self.opp_board.full_animal_just_shot = None

    def check_for_win(self):
        """Returns True if all Animals have been shot.

        Call this right after you take a turn, so we just need to check the opp_board.
        """
        return all(animal.shot for animal in self.opp_board.contents if issubclass(type(animal), Animal))

    def set_win_state(self):
        # Careful here. You have to set status before setting winner if you want the user_home screen to look right.
        self.commit_status(None, Status.COMPLETE)
        self.winner = self.your_name
        self.commit_winner()
        self.db_rep["turn"] = None
