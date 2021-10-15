from dataclasses import dataclass
from kivy.event import EventDispatcher
from kivy.properties import StringProperty


# @dataclass
class User(EventDispatcher):
    """Info about the individual playing on this instance of the app."""
    username = StringProperty("")

    def on_username(self, a, b):
        print(type(a), a)
        print(type(b), b)
        return self.username
