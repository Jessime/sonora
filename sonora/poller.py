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
        Clock.schedule_interval(self.scan_for_state_transitions_on_home_screen, 5)
        Clock.schedule_interval(self.scan_for_new_games_on_home_screen, 5)

        self.bind(polled_opp_finish_turn=self.game.resolve_turn_updates)

    def handle_win(self):
        """Do some sanity checking, then notify everything that there's been a win."""
        winner = self.game.db_rep["winner"]
        if winner is None:
            raise ValueError("It should never be nobody's turn but there isn't a winner. Tell Jessime.")
        self.game.winner = winner["username"]

    def fetch_turn_updates(self, arg1):
        """If it isn't your turn, poll to see if it has become your turn.

        Notes:
            1. This func has a lot of early exits.
            2. This func is bound to a popup that shows on any screen.
        """
        empty_game = self.game.db_rep is None
        if empty_game:
            return
        if self.game.your_turn:
            return
        self.game.db_rep.update()
        fresh_turn = self.game.db_rep["turn"]
        game_over = fresh_turn is None

        if game_over:
            self.handle_win()
            return

        self.game.your_turn = fresh_turn["username"] == self.game.your_name
        self.polled_opp_finish_turn = self.game.your_turn

    def scan_for_state_transitions_on_home_screen(self, arg1):
        """If sitting on the home screen, poll for state changes.

        This checks for two transitions:

        1. SETUP -> ACTIVE
        2. ACTIVE -> COMPLETE

        Note: this was originally more complicated, but why not just always refresh?
        The game has nothing else going on.
        """
        if App.get_running_app().sm.current_screen.name != "user_home":
            return

        remainder = []
        for db_rep in self.user.game_rows:
            db_rep.update()
            winner = db_rep["winner"]
            if winner is not None:
                self.winner = winner["username"]
            else:
                remainder.append(db_rep)

        self.user.game_rows = []
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
