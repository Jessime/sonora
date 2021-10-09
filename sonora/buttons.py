from kivy.app import App
from kivy.uix.button import Button


def switch_to_screen(new_screen, direction="left"):
    screen_manager = App.get_running_app().sm
    screen_manager.transition.direction = direction
    screen_manager.current = new_screen


class GotoLoginScreenBtn(Button):

    def __init__(self, **kwargs):
        super(GotoLoginScreenBtn, self).__init__(**kwargs)
        self.text = "Login"

    def on_press(self):
        switch_to_screen("login")


class GotoCreateAccountBtn(Button):

    def __init__(self, **kwargs):
        super(GotoCreateAccountBtn, self).__init__(**kwargs)
        self.text = "Create Account"

    def on_press(self):
        switch_to_screen("create_account")


class BackStartScreenBtn(Button):

    def __init__(self, **kwargs):
        super(BackStartScreenBtn, self).__init__(**kwargs)
        self.size_hint = (1, .1)
        self.text = "Back"

    def on_press(self):
        switch_to_screen("start", "right")
