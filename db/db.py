"""
This file will manage interactions with our database.
At first, it will just contain stubs that return fake data.
Gradually, we will fill in actual calls to our database.
"""

recipes = {'Pizza': 'American', 'Fried Rice': 'Chinese', 'Sushi': 'Japanese',
           'Kimchi': 'Korean', 'Paella': 'Spanish', 'Pita': 'Mediterranean',
           'Pad Thai': 'Thai', 'Chicken Tikka Masala': 'Indian',
           'Nasi Lemak': 'Malaysian', 'Risotto': 'Italian',
           'Souffle': 'French'}


def get_recipe_names():
    """
    A function to return all the recipe names in the database.
    """
    return list(recipes.keys())


def get_cuisine_types():
    """
    A function to return all the cuisine types in the database.
    """
    return list(recipes.values())


def get_recipe(recipe):
    """
    A function that returns one recipe and their respective cuisine type.
    """
    return recipes.get(recipe)
