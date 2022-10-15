"""
This is the file containing all of the endpoints for our flask app.
The endpoint called `endpoints` will return all available endpoints.
"""

# import time
# import urllib3
# import db.db as db
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
        recipe_name = soup.find(id="article-heading_1-0").get_text().strip()
        if recipe_name == '':
            raise wz.NotFound(f'{website} not found')
        ingr = ""
        directions = ""
        ing_list_soup = soup.find(class_="mntl-structured-ingredients__list")
        for li in ing_list_soup.find_all("li"):
            if (li.text != ""):
                ingr += (li.text[1:(len(li.text)-1)] + ", ")
        ingr = ingr[:(len(ingr)-2)]
        directions_soup = soup.find(id="mntl-sc-block_2-0")
        for li in directions_soup.find_all("li"):
            if (li.text != ""):
                directions += (li.text[1:(len(li.text)-3)])
        directions = directions[1:]
        recipe_to_return = {"recipe_name": recipe_name, "ingredients": ingr,
                            "directions": directions}
        return recipe_to_return


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
