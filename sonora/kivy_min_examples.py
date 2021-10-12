from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

from sonora.buttons import (
    GotoLoginScreenBtn,
    GotoCreateAccountBtn,
    BackStartScreenBtn,
    CreateAccountBtn,
    GotoCreateGameBtn,
    LoginBtn,
)
from sonora.static import UPLINK_CLIENT_KEY

from pprint import pprint

import anvil.server


class CreateGameScreen(Screen):
    """Display all the ongoing games a user currently has."""
    def __init__(self, **kwargs):
        super(CreateGameScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical")

        self.layout.add_widget(Button(text="Create Game"))


class UserHomeScreen(Screen):
    """Display all the ongoing games a user currently has."""
    def __init__(self, **kwargs):
        super(UserHomeScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical")
        self.add_widget(self.layout)
        # TODO implement these, starting with CreateGame
        # games = get_games()
        # games = range(3)
        # for game in games:
        #     self.layout.add_widget(GotoGameBtn(game))

        # blank_space = BoxLayout(size_hint=(1, 1-(.1*len(games))))
        blank_space = BoxLayout(size_hint=(1, .8))
        self.layout.add_widget(blank_space)
        self.layout.add_widget(GotoCreateGameBtn(size_hint=(1, .2)))

class UsernamePassword(GridLayout):
    def __init__(self, **kwargs):
        super(UsernamePassword, self).__init__(**kwargs)
        self.cols = 2
        self.add_widget(Label(text="Username:"))
        self.username = TextInput(multiline=False)
        self.add_widget(self.username)
        self.add_widget(Label(text="Password:"))
        self.password = TextInput(password=True, multiline=False)
        self.add_widget(self.password)


class LoginSpace(BoxLayout):
    def __init__(self, **kwargs):
        super(LoginSpace, self).__init__(**kwargs)
        self.orientation = "vertical"
        self.login_input_space = UsernamePassword()
        self.add_widget(self.login_input_space)
        self.add_widget(LoginBtn())


class CreateAccountSpace(BoxLayout):
    def __init__(self, **kwargs):
        super(CreateAccountSpace, self).__init__(**kwargs)
        self.orientation = "vertical"
        self.create_account_input_space = UsernamePassword()
        self.add_widget(self.create_account_input_space)
        self.add_widget(CreateAccountBtn())


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical")
        self.add_widget(self.layout)
        self.login_space = LoginSpace(size_hint=(1, 0.2))
        self.layout.add_widget(self.login_space)
        self.layout.add_widget(BackStartScreenBtn())
        blank_space = BoxLayout(size_hint=(1, 0.7))
        self.layout.add_widget(blank_space)


class CreateAccountScreen(Screen):
    def __init__(self, **kwargs):
        super(CreateAccountScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical")
        self.add_widget(self.layout)
        self.create_account_space = CreateAccountSpace(size_hint=(1, 0.2))
        self.layout.add_widget(self.create_account_space)
        self.layout.add_widget(BackStartScreenBtn())
        blank_space = BoxLayout(size_hint=(1, 0.7))
        self.layout.add_widget(blank_space)


class StartScreen(Screen):
    def __init__(self, **kwargs):
        super(StartScreen, self).__init__(**kwargs)
        self.layout = GridLayout(cols=2)
        self.add_widget(self.layout)
        self.create_btn = self.layout.add_widget(GotoCreateAccountBtn())
        self.login_btn = self.layout.add_widget(GotoLoginScreenBtn())


class SonoraApp(App):
    def build(self):
        # Create the screen manager
        anvil.server.connect(UPLINK_CLIENT_KEY)
        self.sm = ScreenManager()
        self.sm.add_widget(StartScreen(name="start"))
        self.sm.add_widget(LoginScreen(name="login"))
        self.sm.add_widget(CreateAccountScreen(name="create_account"))
        self.sm.add_widget(UserHomeScreen(name="user_home"))
        self.sm.current = "user_home"  # dev
        return self.sm
