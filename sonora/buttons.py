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


class GotoCreateGameBtn(Button):
    def __init__(self, **kwargs):
        super(GotoCreateGameBtn, self).__init__(**kwargs)
        self.text = "Create Game"

    def on_press(self):
        switch_to_screen("new_game")


class GotoCreateAccountBtn(Button):
    def __init__(self, **kwargs):
        super(GotoCreateAccountBtn, self).__init__(**kwargs)
        self.text = "Create Account"

    def on_press(self):
        switch_to_screen("create_account")


class CreateAccountBtn(Button):
    def __init__(self, **kwargs):
        super(CreateAccountBtn, self).__init__(**kwargs)
        self.text = "Create Account"

    def on_press(self):
        inputs = self.parent.create_account_input_space
        username = inputs.username.text
        password = inputs.password.text
        hashed = bcrypt.hashpw(bytes(password, encoding="utf8"), bcrypt.gensalt())
        anvil.server.call("create_account", username, hashed.decode("utf-8"))
        logger.info(f"Created new account for {username}")


class GotoLoginScreenBtn(Button):
    def __init__(self, **kwargs):
        super(GotoLoginScreenBtn, self).__init__(**kwargs)
        self.text = "Login"

    def on_press(self):
        switch_to_screen("login")


class LoginBtn(Button):
    def __init__(self, **kwargs):
        super(LoginBtn, self).__init__(**kwargs)
        self.text = "Login"

    def on_press(self):
        inputs = self.parent.login_input_space
        username = inputs.username.text
        password = bytes(inputs.password.text, encoding="utf8")
        pass_hash = anvil.server.call("get_pass_hash", username)
        correct_pass = bcrypt.checkpw(password, bytes(pass_hash, encoding="utf-8"))
        if correct_pass:
            logger.info(f"{username} successfully logged in")
            switch_to_screen("user_home")
        else:
            logger.warning(f"Oh no! {password} isn't correct for {username}")
            pass  # TODO implement


class BackStartScreenBtn(Button):
    def __init__(self, **kwargs):
        super(BackStartScreenBtn, self).__init__(**kwargs)
        self.size_hint = (1, 0.1)
        self.text = "Back"

    def on_press(self):
        switch_to_screen("start", "right")
