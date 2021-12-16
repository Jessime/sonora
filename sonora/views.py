from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Rectangle

from sonora.buttons import (
    AnimalButton,
    GotoLoginScreenBtn,
    GotoCreateAccountBtn,
    BackHomeScreenBtn,
    BackStartScreenBtn,
    CreateGameBtn,
    CreateAccountBtn,
    GotoCreateGameBtn,
    LoginBtn,
    ResumeGameBtn,
    GotoNextSetupPart,
    ResetSetup,
    SetupBoardBtn,
)
from sonora.static import SonoraColor, COLS


def set_background_color(label, color):
    """Add a background color to a Label

    Note: Sorry for this piece of magic. It's what's needed since Kivy doesn't have it by default.
    """
    def update_rect(self, instance):
        self.background.pos = self.pos
        self.background.size = self.size

    with label.canvas.before:
        Color(*color.value)
        label.background = Rectangle(size=label.size, pos=label.pos)
    setattr(label, "update_rect", update_rect)
    label.bind(size=label.update_rect, pos=label.update_rect)


class ModelViewer:
    """Can be subclassed by any widget that needs to VIEW data."""
    def __init__(self, **kwargs):
        super(ModelViewer, self).__init__(**kwargs)
        app = App.get_running_app()
        self.user = app.user
        self.animal_types = app.animal_types
        self.game_setup = app.game_setup
        # If I actually run into a bug based on this, I'll figure out enforcement


class NextOrReset(GridLayout):
    def __init__(self, **kwargs):
        super(NextOrReset, self).__init__(**kwargs)
        self.cols = 2
        self.size_hint = (1, 0.1)
        self.add_widget(ResetSetup())
        self.add_widget(GotoNextSetupPart())


class SetupHeader(Label):
    def __init__(self, **kwargs):
        super(SetupHeader, self).__init__(**kwargs)
        self.text = "Choose your board settings for the beginning of the game."
        self.size_hint = (1, 0.1)
        self.color = (0, 0, 0, 1)
        set_background_color(self, SonoraColor.TERMINAL_PAPER)


class SetupLeftUpper(BoxLayout, ModelViewer):
    def __init__(self, **kwargs):
        super(SetupLeftUpper, self).__init__(**kwargs)
        self.add_widget(AnimalButton(self.animal_types.SNAKE))
        set_background_color(self, SonoraColor.MOUSE_FUR)


class SetupLeftLower(BoxLayout, ModelViewer):
    def __init__(self, **kwargs):
        super(SetupLeftLower, self).__init__(**kwargs)
        self.add_widget(AnimalButton(self.animal_types.CENTIPEDE))
        set_background_color(self, SonoraColor.MOUSE_FUR)


class SetupLeft(BoxLayout):
    def __init__(self, **kwargs):
        super(SetupLeft, self).__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = 10
        self.add_widget(SetupLeftUpper())
        self.add_widget(SetupLeftLower())


class InstructionHeader(Label):
    def __init__(self, **kwargs):
        super(InstructionHeader, self).__init__(**kwargs)
        self.text = "Instructions"
        self.color = (0, 0, 0, 1)
        self.size_hint = (1, .2)
        set_background_color(self, SonoraColor.TERMINAL_PAPER)


class Instructions(BoxLayout):
    def __init__(self, **kwargs):
        super(Instructions, self).__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint = (1, 0.5)
        self.add_widget(InstructionHeader())
        txt = ("1. Click the animal you want to place.\n"
               "2. The valid squares for placing the animal will turn green.\n"
               "3. Click a tile on the board to choose the location.\n"
               "    (The tile you click will be the top-left of the animal.)\n"
               "4. Click another tile if you want to relocate the animal.\n"
               "5. Click 'Next' when you are satisfied.")
        self.add_widget(Label(text=txt, size_hint=(1, .8)))


def board_view_generator():
    yield Label(text="")
    for letter in COLS:
        yield Label(text=letter)
    for row in range(1, 11):
        yield Label(text=str(row))
        for col in COLS:
            yield SetupBoardBtn(row, col)


class OuterBoardArea(GridLayout):
    def __init__(self, **kwargs):
        super(OuterBoardArea, self).__init__(**kwargs)
        self.cols = 11
        self.size_hint = (1, 0.5)
        for child in board_view_generator():
            self.add_widget(child)


class SetupRight(BoxLayout):
    def __init__(self, **kwargs):
        super(SetupRight, self).__init__(**kwargs)
        self.orientation = "vertical"
        self.add_widget(Instructions())
        self.add_widget(OuterBoardArea())


class SetupMain(GridLayout):
    def __init__(self, **kwargs):
        super(SetupMain, self).__init__(**kwargs)
        self.cols = 2
        self.size_hint = (1, 0.8)
        self.add_widget(SetupLeft())
        self.add_widget(SetupRight())


class SetupGameScreen(Screen):
    """Choose your board settings for the beginning of the game.

    Note: leaving this screen while in progress will wipe everything.
    This can be useful if you wanna reset the board,
    but could be frustrating if a player closes the window part way through.
    """
    def __init__(self, **kwargs):
        super(SetupGameScreen, self).__init__(**kwargs)
        self.name = "setup_game"
        self.layout = BoxLayout(orientation="vertical")
        self.add_widget(self.layout)
        self.layout.add_widget(SetupHeader())
        self.layout.add_widget(SetupMain())
        self.layout.add_widget(NextOrReset())


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
        set_background_color(self, SonoraColor.TERMINAL_PAPER)
        # with self.canvas.before:
        #     Color(*SonoraColor.TERMINAL_PAPER.value)
        #     self.background = Rectangle(size=self.size, pos=self.pos)

        # self.bind(size=self.update_rect, pos=self.update_rect)
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
    sm.add_widget(SetupGameScreen())
    return sm
