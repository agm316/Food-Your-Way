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
recipe_cuisines = []
recipe_suggestions = []


def get_all():
    """
    Returns all recipes in the database.
    """
    return list(recipes.values())


def get_recipe_names():
    """
    A function to return all the recipe names in the database.
    """
    if len(recipes) == 0:
        return IndexError("There are no recipes in the database!")
    return list(recipes.keys())


def get_recipe(name):
    """
    A function that returns one recipe and their respective information.
    """
    print(recipes)
    if not recipes[name]:
        raise NameError(f'No database entry matches the name: {name}')
    return recipes[name]


def add_recipe(recipe):
    """
    A function to add a recipe to the db
    """
    if not isinstance(recipe, dict):
        raise TypeError(f'Wrong type for recipe: {type(recipe)=}')
    recipes[recipe["recipe_name"]] = recipe
    return True


def del_recipe(recipe):
    """
    A function to remove a recipe from the db
    """
    if not isinstance(recipe, dict):
        raise TypeError(f'Wrong type for recipe: {type(recipe)=}')
    del recipes[recipe["recipe_name"]]
    return True


def get_cuisine_types():
    """
    A function to return all the cuisine types in the database.
    """
    return list(recipe_cuisines.values())
