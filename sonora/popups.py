from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup

from sonora.buttons_dir.popup_btns import CancelBtn, FinishSetupConfirmBtn, NextSetupPageConfirmBtn, TakeTurnConfirmBtn


class NotificationPopup(Popup):
    def __init__(self, message, **kwargs):
        super(NotificationPopup, self).__init__(**kwargs)
        self.title = "Note:"
        self.title_align = "center"
        self.content = Label(text=message)
        self.size_hint = (0.5, 0.5)


class ErrorPopup(Popup):
    def __init__(self, message, **kwargs):
        super(ErrorPopup, self).__init__(**kwargs)
        self.title = "ERROR"
        self.title_align = "center"
        self.content = Label(text=message)
        self.size_hint = (0.5, 0.5)


class ConfirmationContent(BoxLayout):
    def __init__(self, message, **kwargs):
        super(ConfirmationContent, self).__init__(**kwargs)
        self.orientation = "vertical"
        self.add_widget(Label(text=message))
        self.add_widget(CancelBtn())


class NextSetupPageConfirmationContent(ConfirmationContent):
    def __init__(self, message, **kwargs):
        super(NextSetupPageConfirmationContent, self).__init__(message, **kwargs)
        self.add_widget(NextSetupPageConfirmBtn())


class FinishSetupConfirmationContent(ConfirmationContent):
    def __init__(self, message, **kwargs):
        super(FinishSetupConfirmationContent, self).__init__(message, **kwargs)
        self.add_widget(FinishSetupConfirmBtn())


class TakeTurnConfirmationContent(ConfirmationContent):
    def __init__(self, message, **kwargs):
        super(TakeTurnConfirmationContent, self).__init__(message, **kwargs)
        self.add_widget(TakeTurnConfirmBtn())


class ConfirmationPopup(Popup):
    def __init__(self, **kwargs):
        super(ConfirmationPopup, self).__init__(**kwargs)
        self.title = "WARNING"
        self.title_align = "center"
        self.size_hint = (0.5, 0.5)


class NextSetupPageConfirmation(ConfirmationPopup):
    def __init__(self, message, **kwargs):
        super(NextSetupPageConfirmation, self).__init__(**kwargs)
        self.add_widget(NextSetupPageConfirmationContent(message))


class FinishSetupConfirmation(ConfirmationPopup):
    def __init__(self, message, **kwargs):
        super(FinishSetupConfirmation, self).__init__(**kwargs)
        self.add_widget(FinishSetupConfirmationContent(message))


class TakeTurnConfirmation(ConfirmationPopup):
    def __init__(self, message, **kwargs):
        super(TakeTurnConfirmation, self).__init__(**kwargs)
        self.add_widget(TakeTurnConfirmationContent(message))
