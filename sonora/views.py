from kivy.app import App
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from loguru import logger

from sonora.buttons import (
    AnimalButton,
    BackHomeScreenBtn,
    BackStartScreenBtn,
    CreateAccountBtn,
    CreateGameBtn,
    DoSomethingBtn,
    GotoCreateAccountBtn,
    GotoCreateGameBtn,
    GotoLoginScreenBtn,
    GotoNextSetupPartBtn,
    GotoOppBoardBtn,
    GotoYourBoardBtn,
    LoginBtn,
    OppBoardBtn,
    ExitSetupBtn,
    ResumeGameBtn,
    TakeTurnBtn,
    SetupBoardBtn,
    YourBoardBtn,
)
from sonora.buttons_dir.updater import switch_to_screen
from sonora.popups import NotificationPopup
from sonora.static import COLS, SonoraColor, Status, Key


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


def board_view_generator(button_type):
    yield Label(text="")
    for letter in COLS:
        yield Label(text=letter)
    for row in range(1, 11):
        yield Label(text=str(row))
        for col in COLS:
            yield button_type(row, col)


class ModelViewer:
    """Can be subclassed by any widget that needs to VIEW data."""

    def __init__(self, **kwargs):
        super(ModelViewer, self).__init__(**kwargs)
        app = App.get_running_app()
        self.user = app.user
        self.animal_types = app.animal_types
        self.game_setup = app.game_setup
        self.game = app.game
        self.db_poll = app.db_poll
        # If I actually run into a bug based on this, I'll figure out enforcement around "View Only"


class SonoraScreen(Screen):
    """Base class for screens, conveying functionality we want all our screens to have."""

    def __init__(self, **kwargs):
        super(SonoraScreen, self).__init__(**kwargs)

    @property
    def is_current_screen(self):
        current_screen = App.get_running_app().sm.current_screen.name
        return current_screen == self.name


class GameStateHeader(Label, ModelViewer):
    def __init__(self, **kwargs):
        super(GameStateHeader, self).__init__(**kwargs)
        self.color = (0, 0, 0, 1)
        self.size_hint = (1, 0.1)
        set_background_color(self, SonoraColor.TERMINAL_PAPER)
        self.game.bind(your_turn=self.update_text)
        self.update_text(None, self.game.your_turn)

    def update_rect(self, instance, _):
        self.background.pos = instance.pos
        self.background.size = instance.size

    def update_text(self, _, your_turn):
        if your_turn is None:
            return
        turn = "YOUR" if your_turn else "THEIR"
        msg = (f"Welcome to your game with {self.game.opponent}.\n"
               f"It is {turn} turn.")
        self.text = msg


class OuterOppBoardArea(GridLayout):
    def __init__(self, **kwargs):
        super(OuterOppBoardArea, self).__init__(**kwargs)
        self.cols = 11
        for child in board_view_generator(OppBoardBtn):
            self.add_widget(child)


class GameBtnRow(GridLayout):
    def __init__(self, other_board_btn, take_action_btn, **kwargs):
        super(GameBtnRow, self).__init__(**kwargs)
        self.cols = 3
        self.size_hint = (1, 0.1)
        self.add_widget(BackHomeScreenBtn())
        self.add_widget(other_board_btn())
        self.add_widget(take_action_btn())


class OppBoardScreen(SonoraScreen):
    """A place where you can see the state of your board."""

    def __init__(self, **kwargs):
        super(OppBoardScreen, self).__init__(**kwargs)
        self.name = "opp_board"
        self.layout = BoxLayout(orientation="vertical")
        self.add_widget(self.layout)
        self.layout.add_widget(GameStateHeader())

        self.layout.add_widget(OuterOppBoardArea())
        self.layout.add_widget(GameBtnRow(GotoYourBoardBtn, TakeTurnBtn))


class OuterYourBoardArea(GridLayout):
    def __init__(self, **kwargs):
        super(OuterYourBoardArea, self).__init__(**kwargs)
        self.cols = 11
        for child in board_view_generator(YourBoardBtn):
            self.add_widget(child)


class YourBoardScreen(SonoraScreen):
    """A place where you can see the state of your board."""

    def __init__(self, **kwargs):
        super(YourBoardScreen, self).__init__(**kwargs)
        self.name = "your_board"
        self.layout = BoxLayout(orientation="vertical")
        self.add_widget(self.layout)
        self.layout.add_widget(GameStateHeader())

        self.layout.add_widget(OuterYourBoardArea())
        self.layout.add_widget(GameBtnRow(GotoOppBoardBtn, DoSomethingBtn))


class NextOrReset(GridLayout):
    def __init__(self, **kwargs):
        super(NextOrReset, self).__init__(**kwargs)
        self.cols = 2
        self.size_hint = (1, 0.1)
        self.add_widget(ExitSetupBtn())
        self.add_widget(GotoNextSetupPartBtn())


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
        self.animal_button = AnimalButton(self.game_setup.pages[self.game_setup.active_page][0])
        self.add_widget(self.animal_button)
        set_background_color(self, SonoraColor.MOUSE_FUR)
        self.game_setup.bind(active_page=self.update_animal_button)

    def update_animal_button(self, instance, n):
        self.remove_widget(self.animal_button)
        self.animal_button = AnimalButton(self.game_setup.pages[n][0])
        self.add_widget(self.animal_button)


class SetupLeftLower(BoxLayout, ModelViewer):
    def __init__(self, **kwargs):
        super(SetupLeftLower, self).__init__(**kwargs)
        self.animal_button = AnimalButton(self.game_setup.pages[self.game_setup.active_page][1])
        self.add_widget(self.animal_button)
        set_background_color(self, SonoraColor.MOUSE_FUR)
        self.game_setup.bind(active_page=self.update_animal_button)

    def update_animal_button(self, instance, n):
        self.remove_widget(self.animal_button)
        self.animal_button = AnimalButton(self.game_setup.pages[n][1])
        self.add_widget(self.animal_button)


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
        self.size_hint = (1, 0.2)
        set_background_color(self, SonoraColor.TERMINAL_PAPER)


class Instructions(BoxLayout):
    def __init__(self, **kwargs):
        super(Instructions, self).__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint = (1, 0.5)
        self.add_widget(InstructionHeader())
        txt = (
            "1. Click the animal you want to place.\n"
            "2. The valid squares for placing the animal will turn green.\n"
            "3. Click a tile on the board to choose the location.\n"
            "   (The tile you click will be the bottom-left of the animal.)\n"
            "4. Click another tile if you want to relocate the animal.\n"
            "5. Click 'Next' when you are satisfied."
        )
        self.add_widget(Label(text=txt, size_hint=(1, 0.8)))


class OuterSetupBoardArea(GridLayout):
    def __init__(self, **kwargs):
        super(OuterSetupBoardArea, self).__init__(**kwargs)
        self.cols = 11
        self.size_hint = (1, 0.5)
        for child in board_view_generator(SetupBoardBtn):
            self.add_widget(child)


class SetupRight(BoxLayout):
    def __init__(self, **kwargs):
        super(SetupRight, self).__init__(**kwargs)
        self.orientation = "vertical"
        self.add_widget(Instructions())
        self.add_widget(OuterSetupBoardArea())


class SetupMain(GridLayout):
    def __init__(self, **kwargs):
        super(SetupMain, self).__init__(**kwargs)
        self.cols = 2
        self.size_hint = (1, 0.8)
        self.add_widget(SetupLeft())
        self.add_widget(SetupRight())


class SetupGameScreen(Screen, ModelViewer):
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


class CreateGameScreen(SonoraScreen):
    def __init__(self, **kwargs):
        super(CreateGameScreen, self).__init__(**kwargs)
        self.name = "create_game"
        self.layout = BoxLayout(orientation="vertical")
        self.add_widget(self.layout)
        self.layout.add_widget(Label(text="Select the player to challenge", size_hint=(1, 0.1)))
        self.username_space = BoxLayout(orientation="horizontal", size_hint=(1, 0.1))
        self.layout.add_widget(self.username_space)
        self.username_space.add_widget(Label(text="Username:"))
        self.username = TextInput(multiline=False, write_tab=False)
        self.username_space.add_widget(self.username)
        self.create_game_btn = CreateGameBtn()
        self.layout.add_widget(self.create_game_btn)
        self.layout.add_widget(BackHomeScreenBtn())
        self.layout.add_widget(BoxLayout(size_hint=(1, 0.7)))
        Window.bind(on_key_down=self._on_keyboard_down)

    def _on_keyboard_down(self, instance, keyboard, keycode, text, modifiers):
        if self.is_current_screen and keycode == Key.ENTER.value:
            logger.info("Enter key detected. Creating account.")
            self.create_game_btn.on_press()


class Greeting(Label, ModelViewer):
    def __init__(self, **kwargs):
        super(Greeting, self).__init__(**kwargs)
        self.color = (0, 0, 0, 1)
        self.size_hint = (1, 0.1)
        set_background_color(self, SonoraColor.TERMINAL_PAPER)
        self.user.bind(username=self.update_text)

    def update_rect(self, instance, _):
        self.background.pos = instance.pos
        self.background.size = instance.size

    def update_text(self, _, name):
        self.text = f"Hello, {name}"


class IncompleteGames(GridLayout, ModelViewer):
    """Display all the ongoing games a user currently has."""

    def __init__(self, **kwargs):
        super(IncompleteGames, self).__init__(**kwargs)
        self.cols = 4
        self.size_hint = (1, 0.8)
        self.user.bind(game_rows=self.update_game_buttons)

    def update_game_buttons(self, arg1, arg2):
        # Even though only incomplete games are returned on load, a game can become complete afterwards.
        self.clear_widgets()
        for game_row in self.user.game_rows:
            if game_row["status"] == Status.COMPLETE.value:
                continue
            game_btn = ResumeGameBtn(game_row)
            self.add_widget(game_btn)


class UserHomeScreen(SonoraScreen, ModelViewer):
    """Display all the ongoing games a user currently has."""

    def __init__(self, **kwargs):
        super(UserHomeScreen, self).__init__(**kwargs)
        self.name = "user_home"
        self.layout = BoxLayout(orientation="vertical")
        self.add_widget(self.layout)
        self.layout.add_widget(Greeting())

        self.incomplete_games = IncompleteGames()
        self.layout.add_widget(self.incomplete_games)
        self.layout.add_widget(GotoCreateGameBtn())
        self.game.bind(winner=self.announce_win)
        self.db_poll.bind(winner=self.announce_win)

    def announce_win(self, arg1, winner):
        self.incomplete_games.clear_widgets()
        self.incomplete_games.update_game_buttons(None, None)
        if self.is_current_screen:
            switch_to_screen("user_home")
        if winner == self.user.username:
            msg = ("CONGRATULATIONS!\n"
                   "You've photographed all the animals, \n"
                   f"and beaten {self.game.opponent}. \n"
                   "Good job!\n")
        else:
            msg = ("Oh no!\n"
                   f"You've lost your game to {winner}.\n"
                   "Better luck next time.")
        NotificationPopup(msg).open()


class UsernamePassword(GridLayout):
    def __init__(self, **kwargs):
        super(UsernamePassword, self).__init__(**kwargs)
        self.cols = 2
        self.add_widget(Label(text="Username:"))
        self.username = TextInput(multiline=False, write_tab=False)
        self.add_widget(self.username)
        self.add_widget(Label(text="Password:"))
        self.password = TextInput(password=True, multiline=False, write_tab=False)
        self.add_widget(self.password)


class LoginSpace(BoxLayout):
    def __init__(self, **kwargs):
        super(LoginSpace, self).__init__(**kwargs)
        self.orientation = "vertical"
        self.login_input_space = UsernamePassword()
        self.add_widget(self.login_input_space)
        self.login_btn = LoginBtn()
        self.add_widget(self.login_btn)


class CreateAccountSpace(BoxLayout):
    def __init__(self, **kwargs):
        super(CreateAccountSpace, self).__init__(**kwargs)
        self.orientation = "vertical"
        self.create_account_input_space = UsernamePassword()
        self.add_widget(self.create_account_input_space)
        self.create_account_btn = CreateAccountBtn()
        self.add_widget(self.create_account_btn)


class LoginScreen(SonoraScreen):
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
        Window.bind(on_key_down=self._on_keyboard_down)

    def _on_keyboard_down(self, instance, keyboard, keycode, text, modifiers):
        if self.is_current_screen and keycode == Key.ENTER.value:
            logger.info("Enter key detected. Logging in.")
            self.login_space.login_btn.on_press()


class CreateAccountScreen(SonoraScreen):
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
        Window.bind(on_key_down=self._on_keyboard_down)

    def _on_keyboard_down(self, instance, keyboard, keycode, text, modifiers):
        if self.is_current_screen and keycode == Key.ENTER.value:
            logger.info("Enter key detected. Creating account.")
            self.create_account_space.create_account_btn.on_press()


class StartScreen(SonoraScreen):
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
    sm.add_widget(YourBoardScreen())
    sm.add_widget(OppBoardScreen())
    return sm
