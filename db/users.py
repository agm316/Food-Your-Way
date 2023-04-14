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

FIRST_NAME = 'first_name'
LAST_NAME = 'last_name'
EMAIL = 'email'
USERNAME = 'username'
PASSWORD = 'password_hash'
REQUIRED_FIELDS = [FIRST_NAME, LAST_NAME, EMAIL, USERNAME, PASSWORD]


def get_user_details(user):
    """
    Returns a user's details
    """
    dbc.connect_db()
    ret = dbc.fetch_one(USER_COLLECTION, {USER_KEY: user}, USER_DB)
    ret2 = json.loads(json_util.dumps(ret))
    return ret2


def user_exists(user):
    """
    Checks to see if a user exists
    """
    ret = get_user_details(unquote(user))
    return ret is not None


def add_user(user_data):
    """
    Add a user to the DB
    """
    if not isinstance(user_data, dict):
        raise TypeError(f'Wrong type for user_data: {type(user_data)=}')
    dbc.connect_db()
    usr_data = json.loads(json_util.dumps(user_data))
    return dbc.insert_one(USER_COLLECTION, usr_data, USER_DB)
