"""Keeps tabs on updates from the db on a regular cadence. Updates the models as needed."""
import anvil
from kivy.app import App
from kivy.clock import Clock
from kivy.properties import BooleanProperty, StringProperty
from kivy.event import EventDispatcher
from loguru import logger


class DBPoll(EventDispatcher):
    """Methods in this class can directly update the model."""

    # We want to be able to announce a winner from some game
    winner = StringProperty()
    polled_opp_finish_turn = BooleanProperty(defaultvalue=False)

    def __init__(self, game, user, **kwargs):
        super(DBPoll, self).__init__(**kwargs)
        self.game = game
        self.user = user

        Clock.schedule_interval(self.fetch_turn_updates, 3)
        Clock.schedule_interval(self.scan_for_losses_on_home_screen, 3)
        Clock.schedule_interval(self.scan_for_new_games_on_home_screen, 3)

    def fetch_turn_updates(self, arg1):
        """If it isn't your turn, poll to see if it has become your turn."""
        empty_game = self.game.db_rep is None
        if empty_game:
            return
        if self.game.your_turn:
            return
        self.game.db_rep.update()
        fresh_turn = self.game.db_rep["turn"]
        game_over = fresh_turn is None
        if game_over:
            winner = self.game.db_rep["winner"]
            if winner is None:
                raise ValueError("It should never be nobody's turn but there isn't a winner. Tell Jessime.")
            self.game.winner = winner["username"]
        self.game.your_turn = fresh_turn["username"] == self.game.your_name
        self.polled_opp_finish_turn = self.game.your_turn

    def scan_for_losses_on_home_screen(self, arg1):
        """If sitting on the home screen, make sure user hasn't lost any games"""
        if App.get_running_app().sm.current_screen.name != "user_home":
            remainder = []
            found_loss = False
            for db_rep in self.user.game_rows:
                winner = db_rep["winner"]
                if winner is not None:
                    self.winner = winner
                    found_loss = True
            if found_loss:
                self.user.game_rows = remainder

    def scan_for_new_games_on_home_screen(self, arg1):
        """If sitting on the home screen, look for new games"""
        if App.get_running_app().sm.current_screen.name != "user_home":
            return

        def get_usernames(row):
            return frozenset((row["player1"]["username"], row["player2"]["username"])
                             )
        current_games = {get_usernames(row) for row in self.user.game_rows}
        db_games = anvil.server.call("get_incomplete_games", self.user.username)
        new_games = [g for g in db_games if get_usernames(g) not in current_games]
        if new_games:
            logger.info(f"Found {len(new_games)} in db. Adding to games_rows.")
            self.user.game_rows.extend(new_games)
