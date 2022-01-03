import anvil.server
import bcrypt
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.button import Button
from kivy.uix.image import Image
from loguru import logger
from more_itertools import only

from sonora.buttons_dir.updater import ModelUpdater, switch_to_screen
from sonora.models import Game, Segment, SetupStatus, Photo
from sonora.popups import ErrorPopup, FinishSetupConfirmation, NextSetupPageConfirmation, TakeTurnConfirmation, ExitSetupConfirmation
from sonora.static import COLS, SonoraColor
from sonora.data import get_img


class OppBoardBtn(Button, ModelUpdater):
    """

    """
    def __init__(self, row, col, **kwargs):
        super(OppBoardBtn, self).__init__(**kwargs)
        self.row = row
        self.col = col

        self.default_bg = "atlas://data/images/defaulttheme/button"
        self.shot_bg = get_img("green_check.png")
        self.text = f"{col}{str(row)}"
        self.square = None
        self.game.bind(opp_board=self.finish_init_after_board_load)

    def finish_init_after_board_load(self, instance, opp_board):
        self.square = opp_board.grid[(self.row, self.col)]
        self.square.bind(obj=self.update_bg_img)
        # This needs to exist since the square changed before the binding.
        self.update_bg_img(None, self.square.obj)

    def update_bg_img(self, instance, obj):
        """
        One of a few things can happen:

        1. We want to show the default background. That happens if:
            A. There's nothing on that square
            B. There's an undiscovered segment on the square
        2. We want to show a "shot" background. That happens if:
            A. The segment is shot, but the whole animal isn't
        3. We want to show the object image. That happens if:
            A. It's a Photo or something similar
            B. It's a segment is part of an Animal who's been entirely shot
        """
        is_seg = issubclass(type(obj), Segment)
        animal_hidden = is_seg and not obj.animal_backref(self.game.opp_board).shot
        seg_hidden = is_seg and not obj.shot and animal_hidden
        show_shot_seg = is_seg and obj.shot and animal_hidden
        if obj is None or seg_hidden:
            self.background_normal = self.default_bg
            self.text = f"{self.col}{str(self.row)}"
        elif show_shot_seg:
            self.background_normal = self.shot_bg
            self.text = ""
        else:
            self.background_normal = obj.img
            self.text = ""

    def update_model(self, **kwargs):
        self.game.opp_board.clear_of_types(Photo)
        self.game.opp_board + Photo(self.row, self.col)

    def on_press(self):
        """Try to place a Photo"""
        if not self.game.your_turn:
            msg = "You cannot currently take a photo, since it's not your turn."
            ErrorPopup(message=msg).open()
        # Rely on the state of the displayed image, since we don't want to disallow clicking on occupied squares
        elif self.background_normal != self.default_bg:
            ErrorPopup("You have already placed a photo here.").open()
        else:
            self.update_model()


class YourBoardBtn(Button, ModelUpdater):
    """Note: Unless we start adding powers to the animals, this button doesn't do anything."""
    def __init__(self, row, col, **kwargs):
        super(YourBoardBtn, self).__init__(**kwargs)
        self.row = row
        self.col = col

        self.text = f"{col}{str(row)}"
        self.square = None
        self.shot_bg = get_img("x_mark.png")
        self.game.bind(board=self.finish_init_after_board_load)

    def finish_init_after_board_load(self, instance, board):
        # FIXME Something's going wrong here with displaying the your board when you don't close out after setup.
        if self.square is not None:  # We only need to do this once, not everytime the board changes
            return
        self.square = board.grid[(self.row, self.col)]
        self.square.bind(obj=self.update_bg_img)
        # This needs to exist since the square changed before the binding.
        self.update_bg_img(None, self.square.obj)

    def update_bg_img(self, instance, obj):
        """
        Note: This is very similar, but not the same as, `SetupBoardBtn`.
        """
        default = "atlas://data/images/defaulttheme/button"
        if obj is None:
            self.background_normal = default
            self.text = f"{self.col}{str(self.row)}"
        elif issubclass(type(obj), Segment) and obj.shot:
            self.background_normal = self.shot_bg
            self.text = ""
        else:
            self.background_normal = obj.img
            self.text = ""


class SetupBoardBtn(Button, ModelUpdater):
    def __init__(self, row, col, **kwargs):
        super(SetupBoardBtn, self).__init__(**kwargs)
        self.row = row
        self.col = col
        self.text = f"{col}{str(row)}"
        self.default_background_color = self.background_color
        self.game_setup.bind(selected_animal_type=self.update_bg_color)
        self.square = self.game_setup.board.grid[(self.row, self.col)]
        self.square.bind(obj=self.update_bg_img)

    def is_valid_loc(self):
        """Return True if the selected animal can be placed in the this location on the board."""
        segments = self.game_setup.selected_animal_type.cls_segments
        for (rel_row, rel_col), seg in segments.items():
            abs_row = self.row + rel_row
            try:
                abs_col = COLS[COLS.find(self.col) + rel_col]
            except IndexError:
                return False
            out_of_bounds = (abs_row, abs_col) not in self.game_setup.board.grid
            if out_of_bounds:
                return False
            occupied = self.game_setup.board.grid[(abs_row, abs_col)].obj is not None
            if occupied:
                return False
        return True

    def update_bg_color(self, instance, selected_animal_type):
        occupied = self.square.obj is not None
        if occupied or selected_animal_type is None:
            self.background_color = self.default_background_color
            return
        green, red = SonoraColor.SONORAN_SAGE.value, SonoraColor.SEDONA_SUNSET.value
        self.background_color = green if self.is_valid_loc() else red

    def update_bg_img(self, instance, obj):
        """Important side effects:

        1. Calls update_bg_color
        2. Turns on/off showing text
        """
        default = "atlas://data/images/defaulttheme/button"
        self.update_bg_color(None, None)
        if obj is None:
            self.background_normal = default
            self.text = f"{self.col}{str(self.row)}"
        else:
            self.background_normal = obj.img
            self.text = ""

    def update_model(self, new_animal):
        """Add the new animal to the correct location on the board.

        The model can be in one of two states:
        1. Neither of the animals on the page are on the board.
           If so, just place the animal.
        2. An animal from the page is already on the board.
           If so, remove that animal from the board, then place the new one.
           (If it's the same animal, this results in a 'move'.)
        """
        self.game_setup.board.clear_of_types(self.game_setup.avail_types)
        logger.info(f"Placing {new_animal}.")
        for seg in new_animal.segments:
            self.game_setup.board.grid[(seg.row, seg.col)].obj = seg
        self.game_setup.board.contents.append(new_animal)
        logger.info(self.game_setup.board.contents)

    def on_press(self):
        if self.game_setup.selected_animal_type is None:
            logger.info("No animal selected.")
        elif self.is_valid_loc():
            print(self.game_setup.selected_animal_type)
            new_animal = self.game_setup.selected_animal_type(self.row, self.col)
            self.update_model(new_animal)
        else:
            msg = "This is not a valid location for this object."
            ErrorPopup(message=msg).open()


class AnimalButton(ButtonBehavior, Image, ModelUpdater):
    def __init__(self, animal_type, **kwargs):
        super(AnimalButton, self).__init__(**kwargs)
        self.animal_type = animal_type.value
        self.source = self.animal_type.img

    def update_model(self, select=True):
        """'Activate' a particular animal to place on the board.

        Go ahead and clear an existing animal from the page first.
        That way, when the logic bound to the `selected_animal_type` is triggered,
        everything is calculated on a clean board.
        """
        self.game_setup.board.clear_of_types(self.game_setup.avail_types)
        self.game_setup.selected_animal_type = self.animal_type if select else None

    def on_press(self):
        if self.game_setup.selected_animal_type == self.animal_type:
            logger.info(f"De-selected {self.animal_type}")
            self.update_model(False)
        else:
            logger.info(f"Selected {self.animal_type} to place.")
            self.update_model()


class ResumeGameBtn(Button, ModelUpdater):
    def __init__(self, game_row, **kwargs):
        super(ResumeGameBtn, self).__init__(**kwargs)
        self.game_for_btn = Game(game_row, self.user)  # Don't populate `self.game` quite yet
        self.text = f"Resume Game with {self.game_for_btn.opponent}.\n" f"(Status: {self.game_for_btn.status.value})"

    def update_model(self):
        """Populate the "global" `self.game`"""
        self.game.__init__(self.game_for_btn.db_rep, self.user)

    def on_press(self):
        """Try to restart game.

        We can get here from two different ways:
        1. Starting up the app and doing a login.
        2. Finishing setup and being navigated back to the user_home screen.

        If
        """
        # This seems to be necessary for the case where you end up at user_home from Setup.
        self.game_for_btn.setup_status = self.game_for_btn.fetch_setup_status()

        if self.game_for_btn.setup_status == SetupStatus.YOU_DONE_OPP_NOT:
            msg = "You've already completed setup.\n" f"Waiting on {self.game_for_btn.opponent} to finish."
            ErrorPopup(msg).open()
        elif self.game_for_btn.setup_status in (SetupStatus.OPP_DONE_YOU_NOT, SetupStatus.NEITHER):
            self.update_model()
            logger.info(f"Resuming game setup")
            switch_to_screen("setup_game")
        else:
            self.update_model()
            logger.info(f"Resuming game with {self.game.opponent}")
            switch_to_screen("your_board")


class CreateGameBtn(Button, ModelUpdater):
    def __init__(self, **kwargs):
        super(CreateGameBtn, self).__init__(**kwargs)
        self.size_hint = (1, 0.1)
        self.text = "Create Game"
        self.background_color = SonoraColor.SONORAN_SAGE.value

    def update_model(self, game_row, **kwargs):
        self.user.game_rows.append(game_row)

    def on_press(self):
        opponent_name = self.parent.parent.username.text
        if self.user.username == opponent_name:
            ErrorPopup(message="You cannot start a game with yourself.").open()
            return
        row_or_err = anvil.server.call("create_game", self.user.username, opponent_name)
        if isinstance(row_or_err, str):
            ErrorPopup(message=row_or_err).open()
            return
        logger.info(f"Creating a new game with {opponent_name}")
        self.update_model(row_or_err)
        # Important: this line causes the current db row to become the Game
        ResumeGameBtn(row_or_err).on_press()


class GotoCreateGameBtn(Button):
    def __init__(self, **kwargs):
        super(GotoCreateGameBtn, self).__init__(**kwargs)
        self.text = "Create Game"
        self.size_hint = (1, 0.1)
        self.background_color = SonoraColor.SONORAN_SAGE.value

    def on_press(self):
        switch_to_screen("create_game")


class GotoCreateAccountBtn(Button, ModelUpdater):
    def __init__(self, **kwargs):
        super(GotoCreateAccountBtn, self).__init__(**kwargs)
        self.text = "Create Account"
        self.color = (0, 0, 0, 1)
        self.background_normal = get_img("mountains_watercolor1.png")

    def on_press(self):
        switch_to_screen("create_account")


class CreateAccountBtn(Button, ModelUpdater):
    def __init__(self, **kwargs):
        super(CreateAccountBtn, self).__init__(**kwargs)
        self.text = "Create Account"

    def update_model(self, username):
        self.user.username = username

    def on_press(self):
        inputs = self.parent.create_account_input_space
        username = inputs.username.text
        password = inputs.password.text
        hashed = bcrypt.hashpw(bytes(password, encoding="utf8"), bcrypt.gensalt())
        anvil.server.call("create_account", username, hashed.decode("utf-8"))
        logger.info(f"Created new account for {username}")
        self.update_model(username)
        switch_to_screen("user_home")


class GotoLoginScreenBtn(Button):
    def __init__(self, **kwargs):
        super(GotoLoginScreenBtn, self).__init__(**kwargs)
        self.text = "Login"
        self.color = (0, 0, 0, 1)
        self.background_normal = get_img("cactus_watercolor1.png")

    def on_press(self):
        switch_to_screen("login")


class LoginBtn(Button, ModelUpdater):
    def __init__(self, **kwargs):
        super(LoginBtn, self).__init__(**kwargs)
        self.text = "Login"

    def update_model(self, username, games):
        self.user.username = username
        self.user.game_rows = games

    def get_games(self, username):
        pass

    def login(self, username, password):
        password = bytes(password, encoding="utf8")
        pass_hash = anvil.server.call("get_pass_hash", username)
        correct_pass = bcrypt.checkpw(password, bytes(pass_hash, encoding="utf-8"))
        if correct_pass:
            logger.info(f"{username} successfully logged in")
            games = anvil.server.call("get_incomplete_games", username)
            logger.info(f"Found {len(games)} games.")
            self.update_model(username, games)
            switch_to_screen("user_home")
        else:
            msg = f"Oh no! That password isn't correct for {username}."
            ErrorPopup(msg).open()

    def on_press(self):
        inputs = self.parent.login_input_space
        self.login(username=inputs.username.text, password=inputs.password.text)
        self.get_games(inputs.username.text)


class BackStartScreenBtn(Button):
    def __init__(self, **kwargs):
        super(BackStartScreenBtn, self).__init__(**kwargs)
        self.size_hint = (1, 0.1)
        self.text = "Back"

    def on_press(self):
        switch_to_screen("start", "right")


class BackHomeScreenBtn(Button):
    def __init__(self, **kwargs):
        super(BackHomeScreenBtn, self).__init__(**kwargs)
        self.size_hint = (1, 0.1)
        self.text = "Back to Home"
        self.background_color = SonoraColor.SEDONA_SUNSET.value

    def on_press(self):
        switch_to_screen("user_home", "right")


class GotoNextSetupPartBtn(Button, ModelUpdater):
    def __init__(self, **kwargs):
        super(GotoNextSetupPartBtn, self).__init__(**kwargs)
        self.size_hint = (1, 0.1)
        self.text = "Next"
        self.background_color = SonoraColor.SONORAN_SAGE.value

    def update_model(self):
        self.game_setup.active_page += 1

    def on_press(self):
        avail_types = self.game_setup.avail_types
        existing = only((a for a in self.game_setup.board.contents if isinstance(a, avail_types)))
        if existing is None:
            msg = "You must place an animal before continuing."
            ErrorPopup(message=msg).open()
            return
        last = self.game_setup.active_page + 1 == len(self.game_setup.pages)
        if last:
            msg = "Are you finished setting up?\n" "The game will start if you confirm."
            FinishSetupConfirmation(msg).open()
        else:
            msg = "Are you sure you want to continue?\n" "You cannot adjust these animals after."
            NextSetupPageConfirmation(msg).open()


class ExitSetupBtn(Button):
    def __init__(self, **kwargs):
        super(ExitSetupBtn, self).__init__(**kwargs)
        self.size_hint = (1, 0.1)
        self.text = "Exit Board Setup"
        self.background_color = SonoraColor.SEDONA_SUNSET.value

    def on_press(self):
        msg = ("Are you sure you want to exit?\n"
               "Doing so will lose all setup information.")
        ExitSetupConfirmation(msg).open()


class GotoOppBoardBtn(Button):
    def __init__(self, **kwargs):
        super(GotoOppBoardBtn, self).__init__(**kwargs)
        self.size_hint = (1, 0.1)
        self.text = "Go to Opponent's Board"
        self.background_color = SonoraColor.DESERT_RAIN.value

    def on_press(self):
        switch_to_screen("opp_board", "down")


class GotoYourBoardBtn(Button):
    def __init__(self, **kwargs):
        super(GotoYourBoardBtn, self).__init__(**kwargs)
        self.size_hint = (1, 0.1)
        self.text = "Go to Your Board"
        self.background_color = SonoraColor.DESERT_RAIN.value

    def on_press(self):
        switch_to_screen("your_board", "up")


class TakeTurnBtn(Button, ModelUpdater):
    def __init__(self, **kwargs):
        super(TakeTurnBtn, self).__init__(**kwargs)
        self.size_hint = (1, 0.1)
        self.text = "Take Turn"
        self.background_color = SonoraColor.SONORAN_SAGE.value

    def on_press(self):
        photo = only((a for a in self.game.opp_board.contents if isinstance(a, Photo)))
        if photo is None:
            msg = "You must place a photo to take a turn."
            ErrorPopup(msg).open()
        else:
            msg = "Are you sure you want to take your turn?"
            TakeTurnConfirmation(msg).open()


class DoSomethingBtn(Button, ModelUpdater):
    def __init__(self, **kwargs):
        super(DoSomethingBtn, self).__init__(**kwargs)
        self.size_hint = (1, 0.1)
        self.text = "IDK YET"
        self.background_color = SonoraColor.SONORAN_SAGE.value

    def on_press(self):
        print("maybe ask someone else")
