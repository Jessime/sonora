from kivy.uix.button import Button
from loguru import logger

from sonora.static import SonoraColor
from sonora.buttons_dir.updater import ModelUpdater


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


class FinishSetupConfirmBtn(ConfirmBtn):
    def __init__(self, **kwargs):
        super(FinishSetupConfirmBtn, self).__init__(**kwargs)

    def on_press(self):
        logger.info("Finishing setup stage!!")
        self.dismiss_popup()


class CancelBtn(Button):
    def __init__(self, **kwargs):
        super(CancelBtn, self).__init__(**kwargs)
        self.text = "Cancel"
        self.background_color = SonoraColor.SEDONA_SUNSET.value

    def on_press(self):
        self.parent.parent.dismiss()

