import os

import anvil.server
from anvil.tables import app_tables
import anvil.tables.query as q

anvil.server.connect(os.environ["SONORA_UPLINK_KEY"])


@anvil.server.callable
def get_people():
    people = []
    for person in app_tables.users.search():
        people.append(person["email"])
    return people


@anvil.server.callable
def create_account(username, hashed):
    app_tables.users.add_row(username=username, password_hash=hashed, enabled=True)


@anvil.server.callable
def get_pass_hash(username):
    return app_tables.users.get(username=username)["password_hash"]


@anvil.server.callable
def create_game(username, opponent_name):
    user = app_tables.users.get(username=username)
    opponent = app_tables.users.get(username=opponent_name)
    if opponent is None:
        return "This player does not exist in our database. Please try again."
    existing_game = app_tables.games.get(player1=user, player2=opponent)
    if existing_game is not None:
        return "A game between you and this player already exists."

    app_tables.games.add_row(player1=user, player2=opponent, status="SETUP")


@anvil.server.callable
def get_games(username):
    user = app_tables.users.get(username=username)
    games = list(app_tables.games.search(q.any_of(player1=user, player2=user)))
    return games

