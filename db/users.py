"""
This file will be used to manage users in the Mongo Atlas DB.
"""
from urllib.parse import unquote
import json
import bson.json_util as json_util
import db.db_connect as dbc

USER_DB = 'api_dev_db'
USER_COLLECTION = 'users'
USER_KEY = 'user_name'

FIRST_NAME = 'First Name'
LAST_NAME = 'Last Name'
EMAIL = 'Email'
USERNAME = 'Username'
PASSWORD = 'Password'
REQUIRED_FIELDS = [FIRST_NAME, LAST_NAME, EMAIL, USERNAME, PASSWORD]


def get_user_details(user):
    dbc.connect_db()
    ret = dbc.fetch_one(USER_COLLECTION, {USER_KEY: user}, USER_DB)
    ret2 = json.loads(json_util.dumps(ret))
    return ret2
