import anvil.server
from kivy.app import App

from sonora.static import UPLINK_CLIENT_KEY
from sonora.views import get_screen_manager
from sonora.models import User

class SonoraApp(App):
    def build(self):
        # Create the screen manager
        anvil.server.connect(UPLINK_CLIENT_KEY)
        self.user = User()
        self.sm = get_screen_manager()

        return self.sm
