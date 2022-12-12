"""
This module encapsulates details about recipes
"""
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
RECIPE_COLLECT = 'recipes'
REQUIRED_FLDS = [RECIPE_NAME, PREP_TIME, COOK_TIME,
                 PREP_TIME, COOK_TIME, TOTAL_TIME,
                 SERVINGS, YIELD, INGREDIENTS,
                 DIRECTIONS, RATING, URL,
                 CUISINE_PATH, NUTRITION,
                 TIMING, IMG_SRC]


def get_recipe_details(recipe):
    dbc.connect_db()
    return dbc.fetch_one(RECIPE_COLLECT, {RECIPE_KEY: recipe})


def get_time_filter(time):
    dbc.connect_db()
    returns = {}
    ind = 0
    for recipe in dbc.find():
        if recipe["total_time"] <= time:
            returns[ind] = recipe
            ind += 1
    return returns


def recipe_exists(recipe_name):
    """
    Returns whether or not a recipe exists.
    """
    return get_recipe_details(recipe_name) is not None


def get_recipes_dict():
    dbc.connect_db()
    return dbc.fetch_all_as_dict(RECIPE_KEY, RECIPE_COLLECT)


def get_recipes():
    dbc.connect_db()
    return dbc.fetch_all(RECIPE_COLLECT)


def add_recipe(name, recipe_data):
    data = recipe_data
    if not isinstance(name, str):
        raise TypeError(f'Wrong type for name: {type(name)=}')
    if not isinstance(recipe_data, dict):
        raise TypeError(f'Wrong type for recipe_data: {type(recipe_data)=}')
    for field in REQUIRED_FLDS:
        if field not in recipe_data:
            raise ValueError(f'Required {field=} missing from recipe_data')
    dbc.connect_db()
    return dbc.insert_one(RECIPE_COLLECT, data)


def main():
    print("Getting recipes as a list:")
    recipes = get_recipes()
    print(f'{recipes=}')
    print("Getting recipes as a dict:")
    recipes = get_recipes_dict()
    print(f'{recipes=}')


if __name__ == '__main__':
    main()
