import anvil.server
from anvil.tables import app_tables
import bcrypt

anvil.server.connect("EMJPLPV675MUG4U5TW6THWQR-FCSV6U7Z5JICT2KO")
# anvil.server.connect("DLVI5O6VBFTJ5QVEZILJTYLN-FCSV6U7Z5JICT2KO-CLIENT")


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


anvil.server.wait_forever()
