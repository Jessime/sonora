from kivy.uix.button import Button
from loguru import logger

from sonora.buttons_dir.updater import ModelUpdater, switch_to_screen
from sonora.static import SetupStatus, Status, SonoraColor


class ConfirmBtn(Button, ModelUpdater):
    def __init__(self, **kwargs):
        super(ConfirmBtn, self).__init__(**kwargs)
        self.text = "Confirm"
        self.background_color = SonoraColor.SONORAN_SAGE.value

    def dismiss_popup(self):
        self.parent.parent.parent.parent.dismiss()


class NextSetupPageConfirmBtn(ConfirmBtn):
    def __init__(self, **kwargs):
        super(NextSetupPageConfirmBtn, self).__init__(**kwargs)

    def on_press(self):
        self.game_setup.active_page += 1
        logger.info(f"Now on page: {self.game_setup.active_page}")
        self.dismiss_popup()


class FinishSetupConfirmBtn(ConfirmBtn, ModelUpdater):
    def __init__(self, **kwargs):
        super(FinishSetupConfirmBtn, self).__init__(**kwargs)

    def update_model(self, **kwargs):
        self.game.notify_of_setup_finished()
        self.game.board = self.game_setup.board
        if self.game.setup_status == SetupStatus.COMPLETE:
            self.game.status = Status.ACTIVE

    def on_press(self):
        logger.info("Finalizing setup stage!")
        self.update_model()
        self.dismiss_popup()
        if self.game.setup_status == SetupStatus.COMPLETE:
            switch_to_screen("your_board")
        else:
            switch_to_screen("user_home", "right")


class TakeTurnConfirmBtn(ConfirmBtn, ModelUpdater):
    def __init__(self, **kwargs):
        super(TakeTurnConfirmBtn, self).__init__(**kwargs)

    def update_model(self, **kwargs):
        self.game.opp_board.photo_to_shot_or_miss()
        self.game.commit_opp_board(None, self.game.opp_board)
        if self.game.check_for_win():
            self.game.set_win_state()
            switch_to_screen("user_home", "right")
        else:
            self.game.switch_to_opps_turn()

    def on_press(self):
        logger.info("Saving turn.")
        self.update_model()
        self.dismiss_popup()


class CancelBtn(Button):
    def __init__(self, **kwargs):
        super(CancelBtn, self).__init__(**kwargs)
        self.text = "Cancel"
        self.background_color = SonoraColor.SEDONA_SUNSET.value

    def on_press(self):
        self.parent.parent.dismiss()
