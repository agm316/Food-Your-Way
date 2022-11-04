"""
This is the file containing all of the endpoints for our flask app.
The endpoint called `endpoints` will return all available endpoints.
"""

# import time
# import urllib3

import requests
import werkzeug.exceptions as wz
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, url_for, redirect
from flask_restx import Resource, Api, Namespace
from http import HTTPStatus
from pymongo import MongoClient

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from db import db as recdb  # need to fix issue with make prod

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
RATING_ID = "mntl-recipe-review-bar__rating_1-0"
FORMAT = '/format'
DBGETTEST = '/dbtest'
GETALL = '/getallrecipes'
RECIPE_CUISINES_NS = 'recipe_cuisines'
RECIPE_CUISINES_LIST = f'/{LIST}'
RECIPE_CUISINES_LIST_W_NS = f'{RECIPE_CUISINES_NS}/{LIST}'
RECIPE_CUISINES_LIST_NM = f'{RECIPE_CUISINES_NS}_list'
CUISINE_CLASS = "comp mntl-breadcrumbs__item mntl-block"
NUTRITION_CLASS = 'mntl-nutrition-facts-label__table-body type--cat'
TIMING_CLASS = "mntl-recipe-details__content"
TIMING_LABEL = "mntl-recipe-details__label"
TIMING_VALUE = "mntl-recipe-details__value"
IMG_CLASS = ['primary-image__image', 'mntl-primary-image--blurry']

recipe_cuisines = Namespace(RECIPE_CUISINES_NS, 'Recipe Cuisines')
api.add_namespace(recipe_cuisines)


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
        recipe_name = soup.find(id="article-heading_1-0").get_text().strip()
        if recipe_name == '':
            raise wz.NotFound(f'{website} not found')
        prep_time = ""
        cook_time = ""
        total_time = ""
        servings = ""
        ingr = ""
        directions = ""
        rating = ""
        cuisine_path = "/"
        nutr = ""
        timing = ""
        tm_label = ''
        tm_val = ''
        img_src = ""

        # Get Ingredients
        ing_list_soup = soup.find(class_="mntl-structured-ingredients__list")
        for li in ing_list_soup.find_all("li"):
            if (li.text != ""):
                ingr += (li.text[1:(len(li.text)-1)] + ", ")
        if ingr == '':
            raise wz.NotFound("Ingredients Not Found")
        ingr = ingr[:(len(ingr)-2)]

        # Get Directions
        directions_soup = soup.find(id="mntl-sc-block_2-0")
        for li in directions_soup.find_all("li"):
            if (li.text != ""):
                directions += (li.text[1:(len(li.text)-3)])
        if directions == '':
            raise wz.NotFound("Directions Not Found")
        directions = directions[1:]

        # Get Rating (out of 5 stars)
        try:
            rating = soup.find(id=RATING_ID).get_text()
        except Warning:
            pass
        rating = rating.strip()
        # Get Cuisine Path
        cuisine_soup = soup.find_all(class_=CUISINE_CLASS)
        for div in cuisine_soup:
            if (div.text.strip() != "Recipes"):
                cuisine_path = (cuisine_path + div.text.strip() + "/")
        # Get Nutrition Information
        nutr_soup = soup.find(class_=NUTRITION_CLASS)
        for tr in nutr_soup.find_all("tr"):
            if ((tr.text != "") and (tr.text.strip() != "% Daily Value *")):
                tr_list = tr.text.split()
                for i in tr_list:
                    nutr += i + ' '
                nutr = nutr[:(len(nutr)-1)]
                nutr += ', '
        if ((len(nutr) > 1)):
            if (nutr[-2:] == ', '):
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
        # tm_split = timing.split(',')
        # not finished will work on later
        # Get Image URL
        img_soup = soup.find_all("img", class_=IMG_CLASS)
        try:
            img_src = img_soup[0]['src'].strip()
        except Warning:
            pass
        recipe_to_return = {"recipe_name": recipe_name, "prep_time": prep_time,
                            "cook_time": cook_time, "total_time": total_time,
                            "servings": servings, "ingredients": ingr,
                            "directions": directions, "rating": rating,
                            "url": website,
                            "cuisine_path": cuisine_path,
                            "nutrition": nutr,
                            "timing": timing,
                            "img_src": img_src}

        # Recipe gets added to the database for later retrival
        if not recdb.add_recipe(recipe_to_return):
            raise TypeError("Unable to add recipe to the database")
            return False
        return recipe_to_return


@api.route('/getallrecipes')
class getall(Resource):
    """
    This endpoint servers to return all recipes in the
    database and return them as a list of JSONs.
    """
    def get(self):
        return recdb.get_all()


@api.route('/dbtest')
class dbtest(Resource):
    """
    Endpoint to test the data getting from the database
    in the /db/db.py file
    """
    def get(self):
        return recdb.get_recipe("Armenian Pizzas (Lahmahjoon)")


@recipe_cuisines.route(RECIPE_CUISINES_LIST)
class RecipeCuisinesList(Resource):
    """
    This will get a list of recipe cuisines.
    """
    def get(self):
        return {RECIPE_CUISINES_LIST_NM: recdb.get_all()}


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
