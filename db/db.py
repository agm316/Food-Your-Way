"""
This file will manage interactions with our database.
At first, it will just contain stubs that return fake data.
Gradually, we will fill in actual calls to our database.
"""

"""
Testing case Recipe database

recipes = {'Pizza': 'American', 'Fried Rice': 'Chinese', 'Sushi': 'Japanese',
           'Kimchi': 'Korean', 'Paella': 'Spanish', 'Pita': 'Mediterranean',
           'Pad Thai': 'Thai', 'Chicken Tikka Masala': 'Indian',
           'Nasi Lemak': 'Malaysian', 'Risotto': 'Italian',
           'Souffle': 'French'}
"""

recipes = {}


def get_all():
    """
    Returns all recipes in the database.
    """
    allrecipes = []
    for name in list(recipes.keys()):
        allrecipes.append(recipes[name])
    return allrecipes


def get_recipe_names():
    """
    A function to return all the recipe names in the database.
    """
    return list(recipes.keys())


def get_recipe(name):
    """
    A function that returns one recipe and their respective information.
    """
    print(recipes)
    if not recipes[name]:
        raise IndexError(f'No database entry matches the name: {name}')
    return recipes[name]


def add_recipe(recipe):
    """
    A function to add a recipe to the db
    """
    if not isinstance(recipe, dict):
        raise TypeError(f'Wrong type for recipe: {type(recipe)=}')
    recipes[recipe["recipe_name"]] = recipe


def get_cuisine_types():
    """
    A function to return all the cuisine types in the database.
    """
    return list(recipes.values())

# import csv
# from pymongo import MongoClient
#
#
# mongoClient = MongoClient('localhost', 27017)
# print(mongoClient)
# db = mongoClient.october_mug_talk
# db.segment.drop()
# print(db)
#
# header = ["Row", "Name", "Prep Time", "Cook Time", "Total Time", "Servings",
#           "Yield", "Ingredients", "Directions", "url", "Additional Time"]
# csvfile = open('test_recipes.csv', 'r')
# reader = csv.DictReader(csvfile)
#
# for each in reader:
#     row = {}
#     for field in header:
#         row[field] = each[field]
#
#     print(row)
#     db.segment.insert(row)

# import pandas as pd
# from pymongo import MongoClient
#
# client = MongoClient('localhost', 27017)
# database = client['Recipes']
# collection = database['test_recipes']
#
#
# def csv_to_json(filename, header=None):
#      header = ["Row", "Name", "Prep Time", "Cook Time", "Total Time",
#                "Servings", "Yield", "Ingredients", "Directions", "url",
#                "Additional Time"]
#     data = pd.read_csv(filename, header=header)
#     return data.to_dict('records')
#
#
# collection.insert_many(csv_to_json('db/test_recipes.csv'))
