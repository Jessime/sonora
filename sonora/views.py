from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Rectangle

from sonora.buttons import (
    GotoLoginScreenBtn,
    GotoCreateAccountBtn,
    BackHomeScreenBtn,
    BackStartScreenBtn,
    CreateGameBtn,
    CreateAccountBtn,
    GotoCreateGameBtn,
    LoginBtn,
    ResumeGameBtn,
)
from sonora.static import SonoraColor


class ModelViewer:
    """Can be subclassed by any widget that needs to VIEW data."""
    def __init__(self, **kwargs):
        super(ModelViewer, self).__init__(**kwargs)
        root = App.get_running_app()
        self.user = root.user
        # If I actually run into a bug based on this, I'll figure out enforcement


def SetupGameScreen(Screen):
    pass


class CreateGameScreen(Screen):
    def __init__(self, **kwargs):
        super(CreateGameScreen, self).__init__(**kwargs)
        self.name = "create_game"
        self.layout = BoxLayout(orientation="vertical")
        self.add_widget(self.layout)
        self.layout.add_widget(Label(text="Select the player to challenge", size_hint=(1, 0.1)))
        self.username_space = BoxLayout(orientation="horizontal", size_hint=(1, 0.1))
        self.layout.add_widget(self.username_space)
        self.username_space.add_widget(Label(text="Username:"))
        self.username = TextInput(multiline=False)
        self.username_space.add_widget(self.username)
        self.layout.add_widget(CreateGameBtn())
        self.layout.add_widget(BackHomeScreenBtn())
        self.layout.add_widget(BoxLayout(size_hint=(1, .7)))


class Greeting(Label, ModelViewer):
    def __init__(self, **kwargs):
        super(Greeting, self).__init__(**kwargs)
        self.color = (0, 0, 0, 1)
        self.size_hint = (1, .1)
        with self.canvas.before:
            Color(*SonoraColor.TERMINAL_PAPER.value)
            self.background = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self.update_rect, pos=self.update_rect)
        self.user.bind(username=self.update_text)

    def update_rect(self, instance, _):
        self.background.pos = instance.pos
        self.background.size = instance.size

    def update_text(self, _, name):
        self.text = f"Hello, {name}"


class ActiveGames(GridLayout, ModelViewer):
    """Display all the ongoing games a user currently has."""
    def __init__(self, **kwargs):
        super(ActiveGames, self).__init__(**kwargs)
        self.cols = 4
        self.size_hint = (1, .8)
        self.user.bind(game_rows=self.update_game_buttons)

    def update_game_buttons(self, arg1, arg2):
        print(f"{arg1=}, {arg2=}")
        for game in self.user.game_rows:
            opponent = game["player1"] if game["player1"]["username"] == self.user.username else game["player2"]
            game_btn = ResumeGameBtn(opponent["username"], game["status"])
            self.add_widget(game_btn)


class UserHomeScreen(Screen):
    """Display all the ongoing games a user currently has."""
    def __init__(self, **kwargs):
        super(UserHomeScreen, self).__init__(**kwargs)
        self.name = "user_home"
        self.layout = BoxLayout(orientation="vertical")
        self.add_widget(self.layout)
        self.layout.add_widget(Greeting())

        self.layout.add_widget(ActiveGames())
        self.layout.add_widget(GotoCreateGameBtn())


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
        self.name = "login"
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
        self.name = "create_account"
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
        self.name = "start"
        self.layout = GridLayout(cols=2)
        self.add_widget(self.layout)
        self.create_btn = self.layout.add_widget(GotoCreateAccountBtn())
        self.login_btn = self.layout.add_widget(GotoLoginScreenBtn())


def get_screen_manager():
    sm = ScreenManager()
    sm.add_widget(StartScreen())
    sm.add_widget(LoginScreen())
    sm.add_widget(CreateAccountScreen())
    sm.add_widget(UserHomeScreen())
    sm.add_widget(CreateGameScreen())
    return sm
