"""
Upload arbitrary game state to the current game of "jk" vs "jack".

Takes two args:

1. The name of the player to upload to
2. The path to the file that contains the json representation of the board.
"""
import sys
import pickle
import json
from gzip import compress

import anvil.server
from anvil import BlobMedia
from more_itertools import only


name_to_load_to, board_path = sys.argv[1:]

anvil.server.connect("DLVI5O6VBFTJ5QVEZILJTYLN-FCSV6U7Z5JICT2KO-CLIENT")

games = anvil.server.call("get_incomplete_games", "jk")
jk_vs_jack = only(g for g in games if g["player1"]["username"] == "jack" or g["player2"]["username"] == "jack")
col_name = "player1_board" if jk_vs_jack["player1"]["username"] == name_to_load_to else "player1_board"

simple_board = json.load(open(board_path))
jk_vs_jack[col_name] = BlobMedia("text/plain", compress(pickle.dumps(simple_board)))

# more temp?
jk_vs_jack["status"] = "ACTIVE"
jk_vs_jack["turn"] = jk_vs_jack["player2"]
jk_vs_jack["winner"] = None
