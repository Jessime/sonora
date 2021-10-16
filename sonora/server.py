import os

import anvil.server
from anvil.tables import app_tables

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
    opponent = app_tables.users.get(username=opponent_name)
    if opponent is None:
        return "ERROR: opponent missing"
    existing_game = app_tables.games.get(player1=username, player2=opponent_name)
    if existing_game is not None:
        return "ERROR: game already exists"

    app_tables.users.add_row(player1=username, player2=opponent_name, status="SETUP")
