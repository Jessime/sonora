from enum import Enum

from kivy.event import EventDispatcher
from kivy.properties import ObjectProperty
from more_itertools import only

from sonora.data import get_img
from sonora.static import COLS


class BaseBoardObject:
    """Abstract Parent Class for things that go on the board."""

    img = None

    def __init__(self, row, col):
        self.row = row
        self.col = col

    def __repr__(self):
        return f"{self.__class__.__name__}({self.row}, {self.col})"

    @property
    def loc(self):
        return self.row, self.col

    @loc.setter
    def loc(self, value):
        self.row, self.col = value

    def serialize(self):
        """Represent in a json valid format.

        Note: feel free to override for more complicated objects.
        """
        rep = {"class": self.__class__.__name__, "params": {"row": self.row, "col": self.col}, "attrs": {}}
        return rep

    @classmethod
    def deserialize(cls, db_rep):
        new = cls(**db_rep["params"])
        for name, value in db_rep["attrs"].items():
            setattr(new, name, value)
        return new


class Photo(BaseBoardObject):
    """A transient attempt to take a photo of opponent's animal."""

    img = get_img("camera.png")


class Miss(BaseBoardObject):
    img = get_img("saguaro.jpeg")


class Square(EventDispatcher):
    """A single tile on the Board.

    A Square can only contain one object at a time.
    This is mostly for simplicity.
    1. It's how Battleship does it.
    2. There's no good way to visualize multiple objects on a square at the same time.
    """

    obj = ObjectProperty(allownone=True)

    def __init__(self, obj=None, **kwargs):
        super(Square, self).__init__(**kwargs)
        self.obj = obj

    def __repr__(self):
        return "Square[Empty]" if self.obj is None else f"Square[{self.obj}]"


class Segment(BaseBoardObject):
    """A single square of an Animal"""

    def __init__(self, row, col):
        super(Segment, self).__init__(row, col)

        self.shot = False

    def serialize(self):
        self_data = {
            "class": self.__class__.__name__,
            "params": {"row": self.row, "col": self.col},
            "attrs": {"shot": self.shot},
        }
        return self_data

    def animal_backref(self, board):
        """Find the animal a segment belongs to.

        I'm sorry for this piece of magic, but I don't want to store the animal a segment belongs to in the segment.
        Instead, use some string matching based on class names to determine which animal the segment is a part of.
        I've been consistent with naming conventions, so I don't think this will be a cause of bugs."""
        name = self.__class__.__name__
        chars = [name[0]]
        for c in name[1:]:
            if c.islower():
                chars.append(c)
            else:
                break
        animal_cls = globals()["".join(chars)]
        animal = only((a for a in board.contents if isinstance(a, animal_cls)))
        return animal


class Animal:
    # Note: This isn't a BaseBoardObject because it represents multiple squares.
    # If I get far enough that I have anything else besides animals that are multi-square,
    # I should make a parent class that allows you to have a consistent interface for adding/removing from board, etc.
    img = None
    cls_segments = {}

    def __init__(self, base_row, base_col):
        self.base_row = base_row
        self.base_col = base_col

        self.segments = self.make_segments()

    @property
    def shot(self):
        return all(seg.shot for seg in self.segments)

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


class FlycatcherMale(Segment):
    img = get_img("vermilion_flycatcher_male.jpeg")

    def __init__(self, row, col):
        super(FlycatcherMale, self).__init__(row, col)


class FlycatcherFemale(Segment):
    img = get_img("vermilion_flycatcher_female.jpeg")

    def __init__(self, row, col):
        super(FlycatcherFemale, self).__init__(row, col)


class Flycatcher(Animal):
    img = get_img("vermilion_flycatcher.jpeg")
    cls_segments = {
        (0, 0): FlycatcherMale,
        (0, 1): FlycatcherFemale,
    }

    def __init__(self, base_row, base_col):
        super(Flycatcher, self).__init__(base_row, base_col)


class PyrrhuloxiaHead(Segment):
    img = get_img("pyrrhuloxia_head.jpeg")

    def __init__(self, row, col):
        super(PyrrhuloxiaHead, self).__init__(row, col)


class PyrrhuloxiaBody(Segment):
    img = get_img("pyrrhuloxia_body.jpeg")

    def __init__(self, row, col):
        super(PyrrhuloxiaBody, self).__init__(row, col)


class Pyrrhuloxia(Animal):
    img = get_img("pyrrhuloxia.jpeg")
    cls_segments = {
        (0, 0): PyrrhuloxiaBody,
        (-1, 0): PyrrhuloxiaHead,
    }

    def __init__(self, base_row, base_col):
        super(Pyrrhuloxia, self).__init__(base_row, base_col)


class SnakeHead(Segment):
    img = get_img("snake_head.jpeg")

    def __init__(self, row, col):
        super(SnakeHead, self).__init__(row, col)


class SnakeBody(Segment):
    img = get_img("snake_body.jpeg")

    def __init__(self, row, col):
        super(SnakeBody, self).__init__(row, col)


class SnakeTail(Segment):
    img = get_img("snake_tail.jpeg")

    def __init__(self, row, col):
        super(SnakeTail, self).__init__(row, col)


class Snake(Animal):
    img = get_img("snake.jpeg")
    cls_segments = {
        (0, 0): SnakeTail,
        (-1, 0): SnakeBody,
        (-2, 0): SnakeHead,
    }

    def __init__(self, base_row, base_col):
        super(Snake, self).__init__(base_row, base_col)


class CentipedeHead(Segment):
    img = get_img("centipede_head.png")


class CentipedeBody(Segment):
    img = get_img("centipede_body.png")


class CentipedeTail(Segment):
    img = get_img("centipede_tail.png")


class Centipede(Animal):
    img = get_img("centipede.png")
    cls_segments = {
        (0, 0): CentipedeTail,
        (0, 1): CentipedeBody,
        (0, 2): CentipedeHead,
    }

    def __init__(self, base_row, base_col):
        super(Centipede, self).__init__(base_row, base_col)


class JackrabbitEars(Segment):
    img = get_img("jackrabbit_ears.png")


class JackrabbitChest(Segment):
    img = get_img("jackrabbit_chest.png")


class JackrabbitButt(Segment):
    img = get_img("jackrabbit_butt.png")


class Jackrabbit(Animal):
    img = get_img("jackrabbit.png")
    cls_segments = {
        (0, 0): JackrabbitButt,
        (0, 1): JackrabbitChest,
        (-1, 1): JackrabbitEars,
    }

    def __init__(self, base_row, base_col):
        super(Jackrabbit, self).__init__(base_row, base_col)


class GilaHead(Segment):
    img = get_img("gila_head.jpeg")


class GilaBody(Segment):
    img = get_img("gila_body.jpeg")


class GilaTail(Segment):
    img = get_img("gila_tail.jpeg")


class Gila(Animal):
    img = get_img("gila.jpeg")
    cls_segments = {
        (0, 0): GilaHead,
        (0, 1): GilaBody,
        (0, 2): GilaTail,
    }

    def __init__(self, base_row, base_col):
        super(Gila, self).__init__(base_row, base_col)


class JavelinaMouth(Segment):
    img = get_img("javelina_mouth.jpeg")


class JavelinaHead(Segment):
    img = get_img("javelina_head.jpeg")


class JavelinaBack(Segment):
    img = get_img("javelina_back.jpeg")


class JavelinaBottom(Segment):
    img = get_img("javelina_bottom.jpeg")


class Javelina(Animal):
    img = get_img("javelina.jpeg")
    cls_segments = {
        (0, 0): JavelinaMouth,
        (0, 1): JavelinaBottom,
        (-1, 0): JavelinaHead,
        (-1, 1): JavelinaBack,
    }

    def __init__(self, base_row, base_col):
        super(Javelina, self).__init__(base_row, base_col)


class RingtailHead(Segment):
    img = get_img("ringtail_head.jpeg")


class RingtailBody(Segment):
    img = get_img("ringtail_body.jpeg")


class RingtailTail(Segment):
    img = get_img("ringtail_tail.jpeg")


class RingtailTail2(Segment):
    img = get_img("ringtail_tail2.jpeg")


class Ringtail(Animal):
    img = get_img("ringtail.png")
    cls_segments = {
        (0, 0): RingtailHead,
        (0, 1): RingtailBody,
        (0, 2): RingtailTail,
        (1, 2): RingtailTail2,
    }

    def __init__(self, base_row, base_col):
        super(Ringtail, self).__init__(base_row, base_col)


class BighornLhorn(Segment):
    img = get_img("big_horn_sheep_lhorn.jpeg")


class BighornHead(Segment):
    img = get_img("big_horn_sheep_head.jpeg")


class BighornChest(Segment):
    img = get_img("big_horn_sheep_chest.jpeg")


class BighornTorso(Segment):
    img = get_img("big_horn_sheep_torso.jpeg")


class BighornButt(Segment):
    img = get_img("big_horn_sheep_butt.jpeg")


class Bighorn(Animal):
    img = get_img("big_horn_sheep.png")
    cls_segments = {
        (0, 0): BighornButt,
        (0, 1): BighornTorso,
        (0, 2): BighornChest,
        (-1, 1): BighornLhorn,
        (-1, 2): BighornHead,
    }

    def __init__(self, base_row, base_col):
        super(Bighorn, self).__init__(base_row, base_col)


class BobcatFeet(Segment):
    img = get_img("bobcat_feet.jpeg")


class BobcatChest(Segment):
    img = get_img("bobcat_chest.jpeg")


class BobcatHead(Segment):
    img = get_img("bobcat_head.jpeg")


class BobcatButt(Segment):
    img = get_img("bobcat_butt.jpeg")


class BobcatBack(Segment):
    img = get_img("bobcat_back.jpeg")


class Bobcat(Animal):
    img = get_img("bobcat.png")
    cls_segments = {
        (0, 0): BobcatFeet,
        (0, 1): BobcatButt,
        (-1, 0): BobcatChest,
        (-1, 1): BobcatBack,
        (-2, 0): BobcatHead,
    }

    def __init__(self, base_row, base_col):
        super(Bobcat, self).__init__(base_row, base_col)


class AnimalTypes(Enum):
    FLYCATCHER = Flycatcher
    PYRRHULOXIA = Pyrrhuloxia
    SNAKE = Snake
    CENTIPEDE = Centipede
    JAVELINA = Javelina
    RINGTAIL = Ringtail
    BIGHORN = Bighorn
    BOBCAT = Bobcat
    GILA = Gila
    JACKRABBIT = Jackrabbit
