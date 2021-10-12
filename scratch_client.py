import anvil.server
from anvil.tables import app_tables
import bcrypt

anvil.server.connect("DLVI5O6VBFTJ5QVEZILJTYLN-FCSV6U7Z5JICT2KO-CLIENT")

password = bytes("something fun", encoding="utf8")
print(f"{password=}")
hashed = bcrypt.hashpw(password, bcrypt.gensalt())
anvil.server.call("create_account", "jessime", hashed.decode("utf-8"))

pass_hash = anvil.server.call("get_pass_hash", "jessime")
print(pass_hash)
print(bcrypt.checkpw(password, bytes(pass_hash, encoding="utf-8")))
