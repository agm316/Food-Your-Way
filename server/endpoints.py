"""
This is the file containing all of the endpoints for our flask app.
The endpoint called `endpoints` will return all available endpoints.
"""

# import time
# import urllib3
import db.db as recdb
import requests
import werkzeug.exceptions as wz
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, url_for, redirect
from flask_restx import Resource, Api
from http import HTTPStatus
from pymongo import MongoClient


app = Flask(__name__)
api = Api(app)

client = MongoClient('localhost', 27017)

db = client.flask_db
todos = db.todos

HELLO = '/hello'
MESSAGE = 'message'
SCRAPE_WEBSITE = '/scrape'
SEARCH_QUERY = 'Pizza'
RATING_ID = "mntl-recipe-review-bar__rating_1-0"
FORMAT = '/format'
DBGETTEST = '/dbtest'
NUTRITION_CLASS = 'mntl-nutrition-facts-label__table-body type--cat'
TIMING_CLASS = "mntl-recipe-details__content"
TIMING_LABEL = "mntl-recipe-details__label"
TIMING_VALUE = "mntl-recipe-details__value"


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
        return {"name": "string", "ingredients": []}


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
        ingr = ""
        directions = ""
        nutr = ""
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
        rating = ''
        try:
            rating = soup.find(id=RATING_ID).get_text()
        except Warning:
            pass
        rating = rating.strip()
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
        timing = ""
        tm_label = ''
        tm_val = ''
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
        recipe_to_return = {"recipe_name": recipe_name, "ingredients": ingr,
                            "directions": directions, "rating": rating,
                            "nutrition": nutr,
                            "timing": timing}
        # Recipe gets added to the database for later retrival
        recdb.add_recipe(recipe_to_return)
        return recipe_to_return


@api.route('/dbtest')
class dbtest(Resource):
    """
    Endpoint to test the data getting from the database
    in the /db/db.py file
    """
    def get(self):
        return recdb.get_recipe("Armenian Pizzas (Lahmahjoon)")


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
