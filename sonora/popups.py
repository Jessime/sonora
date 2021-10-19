from kivy.uix.popup import Popup
from kivy.uix.label import Label


class ErrorPopup(Popup):
    def __init__(self, message, **kwargs):
        super(ErrorPopup, self).__init__(**kwargs)
        self.title = "ERROR"
        self.title_align = "center"
        self.content = Label(text=message)
        self.size_hint = (.5, .5)

