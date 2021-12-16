import anvil.server
from kivy.app import App

from sonora.static import UPLINK_CLIENT_KEY
from sonora.views import get_screen_manager
from sonora.models import User, AnimalTypes, GameSetup

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

        self.sm = get_screen_manager()

        #temp code
        from sonora.buttons import LoginBtn
        LoginBtn().login("jk", "bad")

        return self.sm
