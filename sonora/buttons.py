from kivy.app import App
from kivy.uix.button import Button
from loguru import logger
import bcrypt
import anvil.server


def switch_to_screen(new_screen, direction="left"):
    logger.info(f"Switching to {new_screen}")
    screen_manager = App.get_running_app().sm
    screen_manager.transition.direction = direction
    screen_manager.current = new_screen


class ModelUpdater:
    """This class conveniently holds the models for the app.

    It also provides a consistent interface through which Buttons can update models.
    Don't add this class directly to any widgets. Subclass it.

    Buttons are repsonsible for overridding the `update` method.
    """

    def __init__(self, **kwargs):
        super(ModelUpdater, self).__init__(**kwargs)
        # If you have another model besides User
        # models = namedtuple("Models", ["user", "games"])
        # self.models = models(root.user, root.games)
        root = App.get_running_app()
        self.user = root.user

    def update_model(self, **kwargs):
        """Override in children as the entrypoint to modifying the models"""
        raise NotImplemented


class CreateGameBtn(Button, ModelUpdater):
    def __init__(self, **kwargs):
        super(CreateGameBtn, self).__init__(**kwargs)
        self.size_hint = (1, .1)
        self.text = "Create Game"

    def on_press(self):
        logger.info("I'm creating a new game")

class GotoCreateGameBtn(Button, ModelUpdater):
    def __init__(self, **kwargs):
        super(GotoCreateGameBtn, self).__init__(**kwargs)
        self.text = "Create Game"
        self.size_hint = (1, .1)

    def on_press(self):
        switch_to_screen("create_game")


class GotoCreateAccountBtn(Button, ModelUpdater):
    def __init__(self, **kwargs):
        super(GotoCreateAccountBtn, self).__init__(**kwargs)
        self.text = "Create Account"

    def on_press(self):
        switch_to_screen("create_account")


class CreateAccountBtn(Button, ModelUpdater):
    def __init__(self, **kwargs):
        super(CreateAccountBtn, self).__init__(**kwargs)
        self.text = "Create Account"

    def update(self, username):
        self.user.username = username

    def on_press(self):
        inputs = self.parent.create_account_input_space
        username = inputs.username.text
        password = inputs.password.text
        hashed = bcrypt.hashpw(bytes(password, encoding="utf8"), bcrypt.gensalt())
        anvil.server.call("create_account", username, hashed.decode("utf-8"))
        logger.info(f"Created new account for {username}")

        switch_to_screen("user_home")


class GotoLoginScreenBtn(Button, ModelUpdater):
    def __init__(self, **kwargs):
        super(GotoLoginScreenBtn, self).__init__(**kwargs)
        self.text = "Login"

    def on_press(self):
        switch_to_screen("login")


class LoginBtn(Button, ModelUpdater):
    def __init__(self, **kwargs):
        super(LoginBtn, self).__init__(**kwargs)
        self.text = "Login"

    def update_model(self, username):
        self.user.username = username
        print(f"{id(self.user)} as name: {self.user.username}")

    def on_press(self):
        inputs = self.parent.login_input_space
        username = inputs.username.text
        password = bytes(inputs.password.text, encoding="utf8")
        pass_hash = anvil.server.call("get_pass_hash", username)
        correct_pass = bcrypt.checkpw(password, bytes(pass_hash, encoding="utf-8"))
        if correct_pass:
            logger.info(f"{username} successfully logged in")
            self.update_model(username)
            switch_to_screen("user_home")
        else:
            logger.warning(f"Oh no! {password} isn't correct for {username}")
            pass  # TODO implement


class BackStartScreenBtn(Button, ModelUpdater):
    def __init__(self, **kwargs):
        super(BackStartScreenBtn, self).__init__(**kwargs)
        self.size_hint = (1, 0.1)
        self.text = "Back"

    def on_press(self):
        switch_to_screen("start", "right")


class BackHomeScreenBtn(Button, ModelUpdater):
    def __init__(self, **kwargs):
        super(BackHomeScreenBtn, self).__init__(**kwargs)
        self.size_hint = (1, 0.1)
        self.text = "Back"

    def on_press(self):
        switch_to_screen("user_home", "right")
