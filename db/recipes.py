"""
This module encapsulates details about recipes
"""
from urllib.parse import unquote
import json
import bson.json_util as json_util
import db.db_connect as dbc

TEST_RECIPE_NAME = 'Test Recipe'
RECIPE_NAME = 'recipe_name'
PREP_TIME = 'prep_time'
COOK_TIME = 'cook_time'
TOTAL_TIME = 'total_time'
SERVINGS = 'servings'
YIELD = 'yield'
INGREDIENTS = 'ingredients'
DIRECTIONS = 'directions'
RATING = 'rating'
URL = 'url'
CUISINE_PATH = 'cuisine_path'
NUTRITION = 'nutrition'
TIMING = 'timing'
IMG_SRC = 'img_src'

RECIPE_KEY = 'recipe_name'
URL_KEY = 'url'
RECIPE_INGR_KEY = 'ingredients'
RECIPE_COLLECT = 'recipes'

RECIPE_DB = 'api_dev_db'
REQUIRED_FIELDS = [RECIPE_NAME, PREP_TIME, COOK_TIME,
                   PREP_TIME, COOK_TIME, TOTAL_TIME,
                   SERVINGS, YIELD, INGREDIENTS,
                   DIRECTIONS, RATING, URL,
                   CUISINE_PATH, NUTRITION,
                   TIMING, IMG_SRC]


def get_recipe_details(recipe):
    dbc.connect_db()
    ret = dbc.fetch_one(RECIPE_COLLECT, {RECIPE_KEY: recipe}, RECIPE_DB)
    # print(f'{ret=}')
    ret2 = json.loads(json_util.dumps(ret))
    # print(f'{ret2=}')
    return ret2


def get_recipe_from_rec_url(rec_url):
    # print('get_recipe_from_rec_url: ' + f'{rec_url=}')
    dbc.connect_db()
    ret = dbc.fetch_one(RECIPE_COLLECT, {URL_KEY: unquote(rec_url)}, RECIPE_DB)
    ret2 = json.loads(json_util.dumps(ret))
    # print('get_recipe_from_rec_url: ' + f'{ret2=}')
    return ret2


def recipe_exists_from_url(rec_url):
    ret = get_recipe_from_rec_url(rec_url)
    # print('recipe_exists_from_url: ' + f'{ret=}')
    return ret is not None


def search_recipe_ingr(search_term, include, exclude):
    """
    Searches for recipes including specific ingredients
    and excluding other ingredients
    include and exclude are lists
    FYI doesn't make sense to search for something
    with the same include and exclude
    query result would be null
    """
    dbc.connect_db()
    # ^(?=.*(?:inc1|inc2|inc3))(?!.*(?:ex1|ex2|ex3)).*$
    # return dbc.fetch_all_filter({ingredients:
    #  {$regex: f'^((?!{exclude}).)*$',$options: 'i'}})
    reg = ''
    search_reg = ''
    query = ''
    # query_search_term = ''
    # query_ingr = ''
    query_ingr_on = 0
    query_search_term_on = 0
    if len(include) > 0:
        query_ingr_on = 1
        reg = reg + '^'
        for x in range(len(include)):
            if include[x] != '':
                reg = reg + f'(?=.*(?:{include[x]}))'
    if len(exclude) > 0:
        query_ingr_on = 1
        if (len(include) == 0):
            reg = reg + '^'
        for y in range(len(exclude)):
            if exclude[y] != '':
                reg = reg + f'(?!.*(?:{exclude[y]}))'
        reg = reg + '.*$'
    # if (query_ingr_on == 1):
    # query_ingr = {"ingredients": {"$regex": reg, "$options": 'i'}}
    if search_term.strip() != '':
        search_term_split = (search_term.strip()).split()
        if len(search_term_split) > 0:
            query_search_term_on = 1
            for x in range(len(search_term_split)):
                search_reg = search_reg + f'(?=.*{search_term_split[x]})'
        # query_search_term = {"recipe_name"
        # : {"$regex": search_reg, "$options": 'i'}}
    if (query_ingr_on == 1) and (query_search_term_on == 1):
        query = {"$and": [
            {"recipe_name": {"$regex": search_reg, "$options": 'i'}},
            {"ingredients": {"$regex": reg, "$options": 'i'}}
        ]}
    elif query_ingr_on == 1:
        query = {"ingredients": {"$regex": reg, "$options": 'i'}}
    elif query_search_term_on == 1:
        query = {"recipe_name": {"$regex": search_reg, "$options": 'i'}}
        # print(query)
    # reg = f'^(?=.*(?:{include}))(?!.*(?:{exclude})).*$'
    # query = {"ingredients": {"$regex": reg, "$options": 'i'}}
    return dbc.fetch_all_filter(RECIPE_COLLECT, query, RECIPE_DB)


def get_time_filter(time):
    dbc.connect_db()
    returns = {}
    ind = 0
    if (time < 0):
        return {}
    for recipe in get_recipes():
        first_time_int = -1
        tot_time = ''
        try:
            tot_time = recipe["total_time"]
        except ValueError:
            tot_time = ''
        if (isinstance(tot_time, int)):
            first_time_int = tot_time
        elif (isinstance(tot_time, str)):
            if (tot_time == ''):
                pass
            tot_time_split = tot_time.split(' ')
            if (len(tot_time_split) == 0):
                pass
            elif (len(tot_time_split) == 1):
                if (tot_time_split[0] == ""):
                    pass
            first_time_str = tot_time_split[0]
            try:
                number = int(first_time_str)
                first_time_int = number
            except ValueError:
                first_time_int = -1
        if (first_time_int == -1):
            pass
        elif first_time_int <= time:
            returns[ind] = recipe
            ind += 1
    return returns


def recipe_exists(recipe_name):
    """
    Returns whether or not a recipe exists.
    """
    # print('recipe_exists: recipe_name: ' + recipe_name)
    # print('recipe_exists: unquote(recipe_name): ' + unquote(recipe_name))
    ret = get_recipe_details(unquote(recipe_name))
    # print('recipe_exists: ' + f'{ret=}')
    return ret is not None


def get_recipes_dict():
    dbc.connect_db()
    return dbc.fetch_all_as_dict(RECIPE_KEY, RECIPE_COLLECT)


def get_recipes():
    dbc.connect_db()
    return dbc.fetch_all(RECIPE_COLLECT)


def add_recipe(name, recipe_data):
    if not isinstance(name, str):
        raise TypeError(f'Wrong type for name: {type(name)=}')
    if not isinstance(recipe_data, dict):
        raise TypeError(f'Wrong type for recipe_data: {type(recipe_data)=}')
    for field in REQUIRED_FIELDS:
        if field not in recipe_data:
            raise ValueError(f'Required {field=} missing from recipe_data')
    dbc.connect_db()
    # print('add_recipe: ' + f'{recipe_data=}')
    recipe_data[RECIPE_NAME] = name
    rec_data = json.loads(json_util.dumps(recipe_data))
    # print('add_recipe: ' + f'{rec_data=}')
    return dbc.insert_one(RECIPE_COLLECT, rec_data, RECIPE_DB)


def delete_recipe_by_name(recipe_name):
    if recipe_exists(unquote(recipe_name)):
        dbc.del_one(RECIPE_COLLECT, {RECIPE_KEY: unquote(recipe_name)})
        return 1
    else:
        return 0


def main():
    print("Getting recipes as a list:")
    recipes = get_recipes()
    print(f'{recipes=}')
    print("Getting recipes as a dict:")
    recipes = get_recipes_dict()
    print(f'{recipes=}')


if __name__ == '__main__':
    main()
