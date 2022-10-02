"""
This is the file containing all of the endpoints for our flask app.
The endpoint called `endpoints` will return all available endpoints.
"""

from http import HTTPStatus
# import time
import requests
from flask import Flask
from flask_restx import Resource, Api
import werkzeug.exceptions as wz
from bs4 import BeautifulSoup
# import urllib3
# import db.db as db

app = Flask(__name__)
api = Api(app)

SCRAPE_WEBSITE = '/scrape'


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
        return {'hello': 'world'}


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


@api.route(f'{SCRAPE_WEBSITE}/<path:website>')
class ScrapeWebsite(Resource):
    """
    This class will scrape a given webpage with a recipe and returns the recipe
    information in a list
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
        recipe_to_return = {"recipe_name": recipe_name}
        return recipe_to_return
