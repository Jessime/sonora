import anvil.server
from kivy.app import App

from sonora.models import AnimalTypes, Game, GameSetup, User
from sonora.static import UPLINK_CLIENT_KEY
from sonora.views import get_screen_manager
from sonora.poller import DBPoll


class SonoraApp(App):
    def build(self):
        anvil.server.connect(UPLINK_CLIENT_KEY)

        # It's unclear if this is the "right" was to do this.
        # But it's working well enough for my needs.
        # Anyway, this is basically the __init__ of the app,
        # since all of these attributes get attached to "root" app.
        # I'm then allowing the Views to read the data from `ModelViewer`,
        # and allowing button actions to update the data via `ModelUpdater`.
        self.user = User()
        self.animal_types = AnimalTypes
        self.game_setup = GameSetup()
        self.game = Game()
        self.db_poll = DBPoll(self.game, self.user)
        self.sm = get_screen_manager()

        # temp code
        from sonora.buttons import LoginBtn, ResumeGameBtn

        # LoginBtn().login("jk", "bad")
        # ResumeGameBtn(self.user.game_rows[0]).on_press()

        return self.sm
