"""
This file will be used to manage users in the Mongo Atlas DB.
"""
from urllib.parse import unquote
import json
import bson.json_util as json_util
import db.db_connect as dbc

USER_DB = 'api_dev_db'
USER_COLLECTION = 'users'
USER_KEY = 'username'

FIRST_NAME = 'first_name'
LAST_NAME = 'last_name'
EMAIL = 'email'
USERNAME = 'username'
PASSWORD = 'password_hash'
REQUIRED_FIELDS = [FIRST_NAME, LAST_NAME, EMAIL, USERNAME, PASSWORD]

TEST_USER_NAME = 'TEST_USERNAME'


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


def add_user(user_name, user_data):
    """
    Add a user to the DB
    """
    if not isinstance(user_name, str):
        raise TypeError(f'Wrong type for user_name: {type(user_name)=}')
    if not isinstance(user_data, dict):
        raise TypeError(f'Wrong type for user_data: {type(user_data)=}')
    for field in REQUIRED_FIELDS:
        if field not in user_data:
            raise ValueError(f'Required {field=} missing from user_data')
    dbc.connect_db()
    user_data[USER_KEY] = user_name
    usr_data = json.loads(json_util.dumps(user_data))
    if not user_exists(user_name):
        return dbc.insert_one(USER_COLLECTION, usr_data, USER_DB)
    else:
        print("users.py:    add_user: USER ALREADY IN DB")


def delete_user(user):
    """
    Deletes a user
    """
    if user_exists(user):
        dbc.del_one(USER_COLLECTION, {USER_KEY: unquote(user)})
        return 1
    else:
        return 0
