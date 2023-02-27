"""
This is the file containing all the endpoints for our flask app.
The endpoint called `endpoints` will return all available endpoints.
"""

# import time
# import urllib3
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, url_for, redirect
from flask_restx import Resource, Api, Namespace
from http import HTTPStatus
from pymongo import MongoClient
from db import db as recdb  # need to fix issue with make prod
from db import recipes as recmongo
from .errs import pswdError
import requests
import werkzeug.exceptions as wz
import json
import bson.json_util as json_util
import hashlib
import bcrypt

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


app = Flask(__name__)
api = Api(app)

client = MongoClient('localhost', 27017)

db = client.flask_db
todos = db.todos

LIST = 'list'
HELLO = '/hello'
MESSAGE = 'message'
SCRAPE_WEBSITE = '/scrape'
SEARCH = '/search'
SEARCH_QUERY = 'Pizza'
EXCLUSION_QUERY = 'carrots'
RATING_ID = "mntl-recipe-review-bar__rating_1-0"
RATING_ID_2 = "mntl-recipe-review-bar__rating_2-0"
FORMAT = '/format'
FORMATTEXTGAME = '/formatTextGame'
DBGETTEST = '/dbtest'
GETALL = '/getAllRecipes'
RECIPE_NAME_ID_1 = "article-heading_1-0"
RECIPE_NAME_ID_2 = "article-heading_2-0"
RECIPE_CUISINES_NS = 'recipe_cuisines'
RECIPE_CUISINES_LIST = f'/{LIST}'
RECIPE_CUISINES_LIST_W_NS = f'{RECIPE_CUISINES_NS}/{LIST}'
RECIPE_CUISINES_LIST_NM = f'{RECIPE_CUISINES_NS}_list'
RECIPE_SUGGESTIONS_NS = 'recipe_suggestions'
RECIPE_SUGGESTIONS_LIST = f'/{LIST}'
RECIPE_SUGGESTIONS_LIST_W_NS = f'{RECIPE_SUGGESTIONS_NS}/{LIST}'
RECIPE_SUGGESTIONS_LIST_NM = f'{RECIPE_SUGGESTIONS_NS}_list'
CUISINE_CLASS = "comp mntl-breadcrumbs__item mntl-block"
INGREDIENTS_ID = "mntl-structured-ingredients__list"
DIRECTIONS_ID = "mntl-sc-block_2-0"
NUTRITION_CLASS = 'mntl-nutrition-facts-label__table-body type--cat'
TIMING_CLASS = "mntl-recipe-details__content"
TIMING_LABEL = "mntl-recipe-details__label"
TIMING_VALUE = "mntl-recipe-details__value"
IMG_CLASS = ['primary-image__image', 'mntl-primary-image--blurry']
IMG_ID2 = "mntl-sc-block-image_1-0-1"
MAIN_MENU_NM = 'Food Your Way Main Menu'
MAIN_MENU = '/main_menu'
GET_ALL_RECIPES = 'getallrecipes'
GET_RECIPE_SUGGESTIONS = 'getrecipesuggestions'
SETTINGS = 'searchUIsettings'
password = ''

recipe_cuisines = Namespace(RECIPE_CUISINES_NS, 'Recipe Cuisines')
api.add_namespace(recipe_cuisines)

recipe_suggestions = Namespace(RECIPE_SUGGESTIONS_NS, 'Recipe Suggestions')
api.add_namespace(recipe_suggestions)


@api.route('/hello')
class HelloWorld(Resource):
    """
    The purpose of the HelloWorld class is to have a simple test to see if the
    app is working at all.
    """
    def get(self):
        """
        A trivial endpoint to see if the server is running.
        It just answers with "hello world."
        """
        return {MESSAGE: 'hello world'}


@api.route('/endpoints')
class Endpoints(Resource):
    """
    This class will serve as live, fetchable documentation of what endpoints
    are available in the system.
    """
    def get(self):
        """
        The `get()` method will return a list of available endpoints.
        """
        endpoints = ''
        # sorted(rule.rule for rule in api.app.url_map.iter_rules())
        return {"Available endpoints": endpoints}


# VERY VERY rudementary system put in place to allow us to test
# login before a working UI, this works with Swagger
@api.route('/login/<path:username>')  # /<path:password>')
class Login(Resource):
    '''
    This is used as the login endpoint.
    '''
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    def get(self, username):
        '''
        The get() method
        Until we have a better system, the password will stay
        commented I guess :(
        '''
        return {"username": username}  # , "password": password}


# This allows testing of the password storing and loging before
# having a workable UI
@api.route('/password/<path:password>')  # /<path:password>')
class Password(Resource):
    '''
    This is used as the login endpoint.
    '''
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    def get(self, password):
        '''
        This takes the password and encrypts it and stores it
        '''
        if not (65 > len(password) > 7):
            raise pswdError(len(password))

        # future improvement to display password strength here

        encoded = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(encoded, salt)

        return {"hashed": hashed.decode("utf-8")}


@api.route('/format')
class DataFormat(Resource):
    """
    This class serves to inform the user on the format of the db
    entries and also servers to assert that the entires are
    of the right form
    """

    def get(self):
        """
        Trivial endpoint at the moment, will update with asserting
        right db entry format later.
        The 'get()' method returns an object holding the formula
        in the form of an array that has every type of entry.
        """
        return {"row": "row", "name": "name", "prep_time": "prep_time",
                "cook_time": "cook_time", "total_time": "total_time",
                "servings": "servings", "yield": "yield", "ingredients": [],
                "directions": [], "url": "url"}


@api.route('/formatTextGame')
class DataFormatTextGame(Resource):
    """
    This class serves to inform the user on the format of the db
    entries and also servers to assert that the entires are
    of the right form
    """

    def get(self):
        """
        Trivial endpoint at the moment, will update with asserting
        right db entry format later.
        The 'get()' method returns an object holding the formula
        in the form of an array that has every type of entry.
        """
        return {'Data': {"row": "row", "name": "name",
                         "prep_time": "prep_time",
                         "cook_time": "cook_time",
                         "total_time": "total_time",
                         "servings": "servings",
                         "yield": "yield", "ingredients": [],
                         "directions": [], "url": "url"},
                'Type': {'Data': 10},
                'Title': {'Title': 'RecipeFormat'}
                }


@api.route(f'/search={SEARCH_QUERY}')
class SearchQuery(Resource):
    """
    This class will return a search query of recipes in the database.
    """
    def get(self):
        """
        The `get()` method will return a list of recipes.
        Later, this will be updated to
        return the HTML page of such a list
        (when React Front-End is being developed)
        """
        return {"Available recipes: CONNECT TO DB!"}


@api.route(f'{SCRAPE_WEBSITE}/<path:website>')
class ScrapeWebsite(Resource):
    """
    This class will scrape a given webpage with a recipe and returns the recipe
    information in a list.
    This class is meant to work with recipes from www.allrecipes.com
    NOTE: On occasion, allrecipes will change the id tags
          they use for their site.
          This means that when that happens, code will
          need to modified to reflect that.
          In order to maximize compatibility,
          this function keeps checking with
          old tags as well as new ones in case
          some recipes don't get transitioned
          over while other ones do (we don't know
          the inner workings/decisions of allrecipes!!!!!).
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    def get(self, website):
        """
        The `get()` method get the html from the website and return
        a dictionary with the recipe info
        """
        html_doc = requests.get(website).content
        soup = BeautifulSoup(html_doc, 'html.parser')
        # Get Recipe Name
        recipe_name = ''
        try:
            recipe_name_test = soup.find(id=RECIPE_NAME_ID_1)
            if (isinstance(recipe_name_test, type(None))):
                pass
            else:
                recipe_name = recipe_name_test.get_text().strip()
        except Warning:
            pass
        if recipe_name == '':
            try:
                recipe_name_test = soup.find(id=RECIPE_NAME_ID_2)
                if (isinstance(recipe_name_test, type(None))):
                    pass
                else:
                    recipe_name = recipe_name_test.get_text().strip()
            except Warning:
                pass
        if recipe_name == '':
            raise wz.NotFound(f'{website} not found')
        prep_time = ""
        cook_time = ""
        total_time = ""
        servings = ""
        yield_val = ""
        ingr = ""
        directions = ""
        rating = ""
        cuisine_path = "/"
        nutr = ""
        timing = ""
        tm_label = ""
        tm_val = ""
        img_src = ""

        # Get Ingredients
        ing_list_soup = soup.find(class_=INGREDIENTS_ID)
        for li in ing_list_soup.find_all("li"):
            if li.text != "":
                ingr += (li.text[1:(len(li.text)-1)] + ", ")
        if ingr == '':
            raise wz.NotFound("Ingredients Not Found")
        ingr = ingr[:(len(ingr)-2)]

        # Get Directions
        directions_soup = soup.find(id=DIRECTIONS_ID)
        for li in directions_soup.find_all("li"):
            if li.text != "":
                directions += (li.text[1:(len(li.text)-3)])
        if directions == '':
            raise wz.NotFound("Directions Not Found")
        directions = directions[1:]

        # Get Rating (out of 5 stars)
        rating_sp = soup.find(id=RATING_ID)
        if (isinstance(rating_sp, type(None))):
            pass
        else:
            rating = rating_sp.get_text().strip()
        if (rating == ""):
            rating_sp = soup.find(id=RATING_ID_2)
            if (isinstance(rating_sp, type(None))):
                pass
            else:
                rating = rating_sp.get_text().strip()
        # Get Cuisine Path
        cuisine_soup = soup.find_all(class_=CUISINE_CLASS)
        for div in cuisine_soup:
            if div.text.strip() != "Recipes":
                cuisine_path = (cuisine_path + div.text.strip() + "/")
        # Get Nutrition Information
        nutr_soup = soup.find(class_=NUTRITION_CLASS)
        for tr in nutr_soup.find_all("tr"):
            if (tr.text != "") and (tr.text.strip() != "% Daily Value *"):
                tr_list = tr.text.split()
                for i in tr_list:
                    nutr += i + ' '
                nutr = nutr[:(len(nutr)-1)]
                nutr += ', '
        if len(nutr) > 1:
            if nutr[-2:] == ', ':
                nutr = nutr[:(len(nutr)-2)]
        # Get Timing
        time_lb_soup = soup.find_all(class_=TIMING_LABEL)
        time_val_soup = soup.find_all(class_=TIMING_VALUE)
        for div in time_lb_soup:
            tm_label += (div.text.strip() + ',')
        tm_label = (tm_label[:len(tm_label)-1])
        for div in time_val_soup:
            tm_val += (div.text.strip() + ',')
        tm_val = (tm_val[:len(tm_val)-1])
        tm_l_lst = tm_label.split(',')
        tm_v_lst = tm_val.split(',')
        for i in range(len(tm_l_lst)):
            timing += tm_l_lst[i].strip()
            timing += ' '
            timing += tm_v_lst[i].strip()
            timing += ', '
        timing = timing[:(len(timing)-2)]
        # Split timing into its individual components
        tm_split = timing.split(',')
        for x in range(len(tm_split)):
            split_indiv = tm_split[x].split(':')
            if split_indiv[0].strip() == "Prep Time":
                prep_time = split_indiv[1].strip()
            elif split_indiv[0].strip() == "Cook Time":
                cook_time = split_indiv[1].strip()
            elif split_indiv[0].strip() == "Total Time":
                total_time = split_indiv[1].strip()
            elif split_indiv[0].strip() == "Servings":
                servings = split_indiv[1].strip()
            elif split_indiv[0].strip() == "Yield":
                yield_val = split_indiv[1].strip()
        # Get Image URL
        img_soup = soup.find_all("img", class_=IMG_CLASS)
        img2_soup = soup.find("img", id=IMG_ID2)
        if len(img_soup) > 0:
            img_src = img_soup[0]['src'].strip()
        elif img2_soup != "":
            img_src = img2_soup['data-src'].strip()
        # Return
        recipe_to_return = {"recipe_name": recipe_name, "prep_time": prep_time,
                            "cook_time": cook_time, "total_time": total_time,
                            "servings": servings, "yield": yield_val,
                            "ingredients": ingr,
                            "directions": directions, "rating": rating,
                            "url": website,
                            "cuisine_path": cuisine_path,
                            "nutrition": nutr,
                            "timing": timing,
                            "img_src": img_src}

        rec_to_ret_json = json.loads(json_util.dumps(recipe_to_return))
        # Check if recipe is in db already based on URL
        if (not (recmongo.recipe_exists_from_url(website))):
            print("Recipe not in DB, adding it...")
            recmongo.add_recipe(recipe_name, rec_to_ret_json)
        else:
            print("Recipe already in DB! NOT ADDING IT AGAIN!")
        # Recipe gets added to the database for later retrieval
        # recmongo.add_recipe(recipe_name, rec_to_ret_json)
        return recipe_to_return


@api.route(MAIN_MENU)
class MainMenu(Resource):
    """
    This Will Deliver Our Main Menu.
    """
    def get(self):
        """
        Gets the main menu.
        """
        return {'Title': MAIN_MENU_NM,
                'Default': 1,
                'Choices': {
                    '1': {'url': f'/{GET_ALL_RECIPES}', 'method': 'get',
                          'text': 'Get All Recipes'},
                    '2': {'url': f'/{GET_RECIPE_SUGGESTIONS}', 'method': 'get',
                          'text': 'Get Recipe Suggestions'},
                    '3': {'url': f'/{FORMATTEXTGAME}', 'method': 'get',
                          'text': 'Get the recipe format'},
                    '4': {'url': f'/{SETTINGS}', 'method': 'get',
                          'text': 'Get search and UI settings'},
                }}


@api.route('/getRecipeSuggestions')
class GetRecipeSuggestions(Resource):
    """
    This endpoint serves to return a dictionary of
    recipe suggestions from the database.
    """

    def get(self):
        return {'Data': {"Cuisine": "Chinese",
                         "Food": "Roasted Pork",
                         "Drink": "Ginger Lime Ice Green Tea"},
                'Type': {'Data': 12},
                'Title': {'Suggestion': 'Chinese Food'}
                }


# reconfigure for react
@api.route('/searchUISettings')
class GetSettings(Resource):
    """
    This endpoint gets current
    search and UI settings.
    """
    def get(self):
        return {'Data': {'BACKGROUND': 'DARK/LIGHT', 'Font': 'Standard'},
                'Type': {'Data': 2},
                'Title': {'UI Settings': 'Example Setting'}}


@api.route('/getAllRecipes')
class GetAll(Resource):
    """
    This endpoint servers to return all recipes in the
    database and return them as a list of JSONs.
    """
    def get(self):
        # return recdb.get_all()
        return recmongo.get_recipes_dict()


@api.route('/searchIncExc/<search_query>')
class SearchIncExc(Resource):
    """
    This endpoint will allow you to search for something while
    excluding specific ingredients,
    or including specific ingredients,
    or both, depending on what you want to do
    note that you can search to include specific ingredients
    and exclude ones as well.
    Format for search will be as follows:
    'search term;:;inclusion1,inclusion2,
    inclusion3;:;exclusion1,exclusion2,exclusion3'
    search with only inclusion:
    'search term;:;inclusion1,inclusion2,inclusion3;:;'
    search with only exclusion:
    'search term;:;;:;exclusion1,exclusion2,exclusion3'
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    def get(self, search_query):
        print(search_query)
        search_split = search_query.split(';:;')
        search_term = ''
        inclusions = ''
        exclusions = ''
        inclusions_list = []
        exclusions_list = []
        try:
            search_term = search_split[0]
        except Warning:
            print("No Search Term")
        try:
            inclusions = search_split[1]
        except Warning:
            print("No Inclusions")
        try:
            exclusions = search_split[2]
        except Warning:
            print("No Exclusions")
        if (inclusions != ''):
            inclusions_list = inclusions.split(',')
        if (exclusions != ''):
            exclusions_list = exclusions.split(',')
        print(search_term)
        for x in range(len(inclusions_list)):
            print(inclusions_list[x])
        for y in range(len(exclusions_list)):
            print(exclusions_list[y])
        # recipe_list = {'1': {"recipe_name": "Soup", "prep_time": "10mins"}}
        # rec_list_to_ret_json = json.loads(json_util.dumps(recipe_list))
        # return rec_list_to_ret_json
        rec_list = {
                    "Armenian Pizzas (Lahmahjoon)": {
                        "recipe_name": "Armenian Pizzas (Lahmahjoon)",
                        "prep_time": "20 mins",
                        "cook_time": "30 mins",
                        "total_time": "50 mins",
                        "servings": "3",
                        "yield": "6 pizzas",
                        "ingredients": "example ing 1",
                        "directions": "directions",
                        "rating": "4.5",
                        "url": "https://www.allrecipes.com/recipe/154315/a",
                        "cuisine_path": "/Meat and Poultry/Lamb/Ground/",
                        "nutrition": "Total Fat 33g 42%, Potassium 1003mg 21%",
                        "timing": "Prep Time: 20 mins, Cook Time: 30 mins",
                        "img_src": "https://www.allrecipes.comb8d4eb9c02.jpg"
                        },
                    "Chef John's Fresh Salmon Cakes": {
                        "recipe_name": "Chef John's Fresh Salmon Cakes",
                        "prep_time": "20 mins",
                        "cook_time": "15 mins",
                        "total_time": "1 hrs 35 mins",
                        "servings": "4",
                        "yield": "4 salmon cakes",
                        "ingredients": "1 tablespoon extra-virgin olive oil",
                        "directions": "Heat extra virgin olive oil in ",
                        "rating": "4.8",
                        "url": "https://www.allrecipes.cocakes/",
                        "cuisine_path": "/Main Dishes/Seafood Main Dishes/",
                        "nutrition": "Total Fat 34g 43%, Total Carbohydrate",
                        "timing": "Prep Time: 20 mins, Cook Time: 15 mins",
                        "img_src": "https://www.allr98ee1cb0044994758.jpg"
                        }
                    }
        rec_list_jsonified = json.loads(json_util.dumps(rec_list))
        return rec_list_jsonified


@api.route('/filterByCalories')
class FilterByCalories(Resource):
    """
    This endpoint will allow you to filter by calories for all
    the recipes.
    """
    def get(self):
        return {'Data': {"Cuisine": "Chinese",
                         "Food": "Roasted Pork",
                         "Drink": "Ginger Lime Ice Green Tea",
                         "Calories": "1003"},
                'Type': {'Data': 12},
                'Title': {'Suggestion': 'Chinese Food'}
                }


@api.route('/filterByDietType')
class FilterByDietType(Resource):
    """
    This endpoint will allow you to filter by specific diet types
    that people might fall under.
    """
    def get(self):
        return {'Type': {'Vegetarian', 'Vegan', 'Pescatarian'}
                }


@api.route('/dbtest')
class DbTest(Resource):
    """
    Endpoint to test the data getting from the database
    in the /db/db.py file
    """
    def get(self):
        return recmongo.get_recipe_details("Armenian Pizzas (Lahmahjoon)")


@recipe_cuisines.route(RECIPE_CUISINES_LIST)
class RecipeCuisinesList(Resource):
    """
    This will get a list of recipe cuisines.
    """
    def get(self):
        return {RECIPE_CUISINES_LIST_NM: recdb.get_all()}


@recipe_suggestions.route(RECIPE_SUGGESTIONS_LIST)
class RecipeSuggestionsList(Resource):
    """
    This will get a list of recipe suggestions.
    """
    def get(self):
        return {RECIPE_SUGGESTIONS_LIST_NM: recdb.get_all()}


@api.route('/recipes')
class Database(Resource):
    """
    An endpoint to see the requests being sent to the MongoDB database.
    """
    def get(self):
        return "This is the database endpoint.", 200


@app.route('/recipes', methods=('GET', 'POST'))
def index():
    if request.method == 'POST':
        content = request.form['content']
        degree = request.form['degree']
        todos.insert_one({'content': content, 'degree': degree})
        return redirect(url_for('index'))

    all_todos = todos.find()
    return render_template('index.html', todos=all_todos)


# adding in a basic hashing algorithm for a user's password
# will add to this when working with the login system
def md5(user_password):
    result = hashlib.md5(user_password.encode())
    return result.hexdigest()
