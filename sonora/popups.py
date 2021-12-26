from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup

from sonora.buttons_dir.popup_btns import CancelBtn, FinishSetupConfirmBtn, NextSetupPageConfirmBtn


class NotificationPopup(Popup):
    def __init__(self, **kwargs):
        super(NotificationPopup, self).__init__(**kwargs)
        self.title = "Note:"
        self.title_align = "center"
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


#
# class IsFirstPlayer(NotificationPopup):
#     def __init__(self, **kwargs):
#         super(IsFirstPlayer, self).__init__(**kwargs)
#         msg = "Congratulations! You were chosen to be the first player.\n" "Please take your opening move now."
#         self.content = Label(text=msg)
#
#
# class IsSecondPlayer(NotificationPopup):
#     def __init__(self, **kwargs):
#         super(IsSecondPlayer, self).__init__(**kwargs)
#         msg = (
#             "You have been chosen to be the second player.\n"
#             "We will notify you when your opponent has taken their turn."
#         )
#         self.content = Label(text=msg)
