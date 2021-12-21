from kivy.app import App


class ModelUpdater:
    """This class conveniently holds the models for the app.

    It also provides a consistent interface through which Buttons can update models.
    Don't add this class directly to any widgets. Subclass it.

    Buttons are responsible for overriding the `update_model` method.
    """

    def __init__(self, **kwargs):
        super(ModelUpdater, self).__init__(**kwargs)
        # If you have another model besides User
        # models = namedtuple("Models", ["user", "games"])
        # self.models = models(root.user, root.games)
        app = App.get_running_app()
        self.user = app.user
        self.animal_types = app.animal_types
        self.game_setup = app.game_setup

    def update_model(self, **kwargs):
        """Override in children as the entrypoint to modifying the models"""
        raise NotImplemented