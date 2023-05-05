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
PASSWORD = 'hashed_password'

SAVED_RECIPES = 'saved_recipes'
REQUIRED_FIELDS = [FIRST_NAME, LAST_NAME, EMAIL, USERNAME, PASSWORD, SAVED_RECIPES]


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
        dbc.connect_db()
        dbc.del_one(USER_COLLECTION, {USER_KEY: unquote(user)})
        return 1
    else:
        return 0


def update_user_password(username, new_password):
    """
    updates the password for a user
    old_password, new_password are hashes
    """
    new_pass = ''
    user_name = ''
    ret = {}
    dbc.connect_db()
    if isinstance(new_password, str):
        new_pass = new_password.strip()
    if isinstance(username, str):
        user_name = username.strip()
    ret["username"] = user_name
    if user_name == '':
        ret["success"] = 0
        ret["message"] = "Username Is Blank"
        return ret
    if not (user_exists(user_name.strip())):
        ret["success"] = 0
        ret["message"] = "User Does Not Exist"
        return ret
    if new_pass == '':
        ret["success"] = 0
        ret["message"] = "New Password is Blank"
        return ret
    else:
        fltr = {'username': user_name}
        newvals = {"$set": {f'{PASSWORD}': new_pass}}
        dbc.update_one(USER_COLLECTION, fltr, newvals, USER_DB)
        ret["success"] = 1
        ret["message"] = "Password Successfully Updated"
        return ret


def add_saved_recipe(username, recipeid):
    """
    adds a recipe to the user's record
    in mongodb in their saved recipes
    """
    user_name = ''
    recipe_id = ''
    ret = {}
    dbc.connect_db()
    if isinstance(username, str):
        user_name = username.strip()
    if isinstance(recipeid, str):
        recipe_id = recipeid.strip()
    ret["username"] = user_name
    ret["recipe_id"] = recipe_id
    if user_name == '':
        ret["success"] = 0
        ret["message"] = "Username Is Blank"
        return ret
    if not (user_exists(user_name)):
        ret["success"] = 0
        ret["message"] = "User Does Not Exist"
        return ret
    if recipe_id == '':
        ret["success"] = 0
        ret["message"] = "Recipe ID is Blank"
        return ret
    else:
        uservals = get_user_details(user_name)
        old_saved_recipes = (uservals[SAVED_RECIPES]).strip()
        new_saved_recipes = ''
        if old_saved_recipes == '':
            new_saved_recipes = recipe_id + ';'
        else:
            old_recs_lst = old_saved_recipes.split(';')
            already_saved = False
            for x in old_recs_lst:
                if x == recipe_id:
                    already_saved = True
            if already_saved:
                ret["message"] = "Recipe Already Saved in Your Profile"
                # marking success in this case as 1 since the user
                # wanted the recipe in their saved and it is actually there
                ret["success"] = 1
                return ret
            else:
                rec_list_redone = ''
                for y in old_recs_lst:
                    rec_list_redone = rec_list_redone + y.strip() + ';'
                new_saved_recipes = rec_list_redone + recipe_id + ';'
        fltr = {'username': user_name}
        newvals = {"$set": {f'{SAVED_RECIPES}': new_saved_recipes}}
        dbc.update_one(USER_COLLECTION, fltr, newvals, USER_DB)
        ret["success"] = 1
        ret["message"] = "Password Successfully Updated"
        return ret


def remove_saved_recipe(username, recipeid):
    """
    Removes a saved recipe from list of saved recipes
    for a given username
    """
    user_name = ''
    recipe_id = ''
    ret = {}
    dbc.connect_db()
    if isinstance(username, str):
        user_name = username.strip()
    if isinstance(recipeid, str):
        recipe_id = recipeid.strip()
    ret["username"] = user_name
    ret["recipe_id"] = recipe_id
    if user_name == '':
        ret["success"] = 0
        ret["message"] = "Username Is Blank"
        return ret
    if not (user_exists(user_name)):
        ret["success"] = 0
        ret["message"] = "User Does Not Exist"
        return ret
    if recipe_id == '':
        ret["success"] = 0
        ret["message"] = "Recipe ID is Blank"
        return ret
    else:
        uservals = get_user_details(user_name)
        old_saved_recipes = (uservals[SAVED_RECIPES]).strip()
        if old_saved_recipes == '':
            ret["message"] = "No recipes saved for this username. No Changes"
            # since that recipe was asked to be removed,
            # since it is not there, we say we were successful
            ret["success"] = 1
            return ret
        else:
            old_recs_lst = old_saved_recipes.split(';')
            rec_found = False
            new_rec_lst = []
            for x in old_recs_lst:
                if x == recipe_id:
                    rec_found = True
                else:
                    new_rec_lst.append(x)
            if rec_found:
                verify = False
                for y in new_rec_lst:
                    if y == recipe_id:
                        verify = True
                if verify:
                    ret["message"] = "Error removing from list (1)"
                    ret["success"] = 0
                    return ret
                else:
                    new_lst_str = ''
                    for z in new_rec_lst:
                        new_lst_str = new_lst_str + z + ';'
                    fltr = {'username': user_name}
                    newvals = {"$set": {f'{SAVED_RECIPES}': new_lst_str}}
                    dbc.update_one(USER_COLLECTION, fltr, newvals, USER_DB)
                    ret["success"] = 1
                    ret["message"] = "Saved Recipe Successfully Removed"
                    return ret


def remove_all_saved_recipes(username):
    """
    Removes all saved recipes from list of saved recipes
    for a given username
    """
    user_name = ''
    ret = {}
    dbc.connect_db()
    if isinstance(username, str):
        user_name = username.strip()
    ret["username"] = user_name
    if user_name == '':
        ret["success"] = 0
        ret["message"] = "Username Is Blank"
        return ret
    if not (user_exists(user_name)):
        ret["success"] = 0
        ret["message"] = "User Does Not Exist"
        return ret
    else:
        uservals = get_user_details(user_name)
        old_saved_recipes = (uservals[SAVED_RECIPES]).strip()
        if old_saved_recipes == '':
            ret["message"] = "No recipes saved for this username. No changes"
            ret["success"] = 1
            return ret
        else:
            fltr = {'username': user_name}
            newvals = {"$set": {f'{SAVED_RECIPES}': ''}}
            dbc.update_one(USER_COLLECTION, fltr, newvals, USER_DB)
            ret["success"] = 1
            ret["message"] = "All Saved Recipes Successfully Removed"
            return ret
