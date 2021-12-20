from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from sonora.static import SonoraColor


class ErrorPopup(Popup):
    def __init__(self, message, **kwargs):
        super(ErrorPopup, self).__init__(**kwargs)
        self.title = "ERROR"
        self.title_align = "center"
        self.content = Label(text=message)
        self.size_hint = (.5, .5)


class ConfirmBtn(Button):
    def __init__(self, **kwargs):
        super(ConfirmBtn, self).__init__(**kwargs)
        self.text = "Confirm"
        self.background_color = SonoraColor.SONORAN_SAGE.value

    def on_press(self):
        print('why is this not clicking')
        self.parent.confirmed = True


class CancelBtn(Button):
    def __init__(self, **kwargs):
        super(CancelBtn, self).__init__(**kwargs)
        self.text = "Cancel"
        self.background_color = SonoraColor.SEDONA_SUNSET.value

    def on_press(self):
        self.parent.dismiss()


class ConfirmationContent(BoxLayout):
    def __init__(self, message, **kwargs):
        super(ConfirmationContent, self).__init__(**kwargs)
        self.orientation = "vertical"
        self.add_widget(Label(text=message))
        self.add_widget(CancelBtn())
        self.add_widget(ConfirmBtn())


class ConfirmationPopup(Popup):
    def __init__(self, message, **kwargs):
        super(ConfirmationPopup, self).__init__(**kwargs)
        self.title = "WARNING"
        self.title_align = "center"
        # self.content = Label(text=message)
        self.size_hint = (.5, .5)
        self.confirmed = False
        self.content = ConfirmationContent(message)

