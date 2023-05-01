"""
This is the file containing all the endpoints for our flask app.
The endpoint called `endpoints` will return all available endpoints.
"""

# import time
# import urllib3
from bs4 import BeautifulSoup
from flask import Flask, request
from flask_restx import Resource, Api, Namespace, abort
# , fields
from http import HTTPStatus
from pymongo import MongoClient
from db import recipes as recmongo
from db import users as usermongo
from urllib.parse import unquote
from flask_cors import CORS
# from urllib.parse import quote
from .errs import pswdError
import requests
import werkzeug.exceptions as wz
import json
import bson.json_util as json_util
import hashlib
import bcrypt
import re

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

app = Flask(__name__)
CORS(app)
api = Api(app)

client = MongoClient('localhost', 27017)

db = client.flask_db
todos = db.todos

RECIPES_NS = 'recipes'
USERS_NS = 'users'

recipes = Namespace(RECIPES_NS, 'Recipes')
api.add_namespace(recipes)

users = Namespace(USERS_NS, 'Users')
api.add_namespace(users)

LIST = 'list'
RECIPES_LIST = f'/{LIST}'
RECIPES_LIST_W_NS = f'{RECIPES_NS}/{LIST}'
RECIPES_LIST_NM = f'{RECIPES_NS}_list'
RECIPES_CUISINES_LIST_NM = f'{RECIPES_NS}_list'
RECIPES_SUGGESTIONS_LIST_NM = f'{RECIPES_NS}_list'

HELLO = '/hello'
MESSAGE = 'message'
SCRAPE_WEBSITE = '/scrape'
SEARCH = '/search'
SEARCH_QUERY = 'Pizza'
EXCLUSION_QUERY = 'carrots'
RATING_ID = "mntl-recipe-review-bar__rating_1-0"
RATING_ID_2 = "mntl-recipe-review-bar__rating_2-0"
FORMAT = '/recipes/format'
FORMATTEXTGAME = '/formatTextGame'
DBGETTEST = '/dbtest'
GETALL = '/recipes/getAllRecipes'
RECIPE_NAME_ID_1 = "article-heading_1-0"
RECIPE_NAME_ID_2 = "article-heading_2-0"
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
ALL_REC_URL_START = 'https://www.allrecipes.com/'
URL_REC_SUB_TARGET = 'recipe/'
SEARCH_HATEOAS = '/searchHateoas'
SEARCH_HATEOAS_TITLE = 'Recipe Options'
VEG_REC = '/searchIncExc/Vegetarian;:;;:;'
NEW_RECIPES_URL = 'https://www.allrecipes.com/'
NEW_RECIPES_URL = NEW_RECIPES_URL + 'recipes/22908/everyday-cooking'
NEW_RECIPES_URL = NEW_RECIPES_URL + '/special-collections/new/'
SEARCH_TERMS_FILE_NAME = '/search_terms.txt'
DB_MESSAGE_NOT = 'Recipe already in DB! NOT ADDING IT AGAIN!'
HSHD_PWD_KEY = "hashed_password"
PASS_SUCCESS_MESSAGE = "Password Successfully Updated!!!"
INCORRECT_OLD_PWD = "Incorrect Old Password; Can't Update"


def text_strip(text):
    """
    This function strips whitespace off ends of text
    """
    if isinstance(text, type(None)):
        return ''
    elif type(text) == str:
        return text.strip()


def hash_pwd(password):
    """
    This function hashes passwords used for login
    """
    encoded = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(encoded, salt)
    return hashed.decode("utf-8")


# adding in a basic hashing algorithm for a user's password
# will add to this when working with the login system
def md5(user_password):
    result = hashlib.md5(user_password.encode())
    return result.hexdigest()


def load_search_terms(file_name):
    """
    this function loads the search terms
    from search_terms.txt and returns
    a list of search terms
    """
    ret_list = []
    ppath = os.path.dirname(__file__)
    file_path = ppath + file_name
    search_terms_file = open(file_path, 'r')
    for line in search_terms_file:
        ret_list.append(line.strip())
    search_terms_file.close()
    return ret_list


def search_later_pages(website):
    """
    searches later pages for url's or recipes
    and returns a list of them
    """
    len_url_start = len(ALL_REC_URL_START)
    len_sub_url = len(URL_REC_SUB_TARGET)
    html_doc = requests.get(website).content
    soup = BeautifulSoup(html_doc, 'html.parser')
    link_lst = []
    for link in soup.find_all('a', href=True):
        link_i = link.get('href')
        if (((link_i[0:len_url_start]) == ALL_REC_URL_START) and
            ((link_i[len_url_start:(len_sub_url+len_url_start)]) ==
             URL_REC_SUB_TARGET)):
            link_lst.append(link.get('href'))
    return link_lst


def scrape_website_soup(soup, website):
    # Get Recipe Name
    recipe_name = ''
    try:
        recipe_name_test = soup.find(id=RECIPE_NAME_ID_1)
        if isinstance(recipe_name_test, type(None)):
            pass
        else:
            recipe_name = recipe_name_test.get_text().strip()
    except Warning:
        pass
    if recipe_name == '':
        try:
            recipe_name_test = soup.find(id=RECIPE_NAME_ID_2)
            if isinstance(recipe_name_test, type(None)):
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
    if isinstance(rating_sp, type(None)):
        pass
    else:
        rating = rating_sp.get_text().strip()
    if rating == "":
        rating_sp = soup.find(id=RATING_ID_2)
        if isinstance(rating_sp, type(None)):
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
    if not isinstance(nutr_soup, type(None)):
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
    elif isinstance(img2_soup, type(None)):
        pass
    elif img2_soup != "":
        img_src = img2_soup['data-src'].strip()
    # print("recipe_name = " + recipe_name)
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
    # print("recipe_name2 = " + rec_to_ret_json["recipe_name"])
    return rec_to_ret_json


def search_all_rec_from_query(search_query):
    link_lst = []
    query_str = ''
    terms_url_ready = ""
    len_url_start = len(ALL_REC_URL_START)
    len_sub_url = len(URL_REC_SUB_TARGET)
    query_url = "https://www.allrecipes.com/search?q="
    second_p_url = "https://www.allrecipes.com/search?"
    subsequent_url_base = ''
    term_lst = (search_query.strip()).split()
    if len(term_lst) == 0:
        print("No Search Terms")
        return []
    else:
        for x in range(len(term_lst)):
            query_str = query_str + term_lst[x] + '+'
            terms_url_ready = terms_url_ready + term_lst[x]
            terms_url_ready = terms_url_ready + '%20'
        query_str = query_str[:-1]
        terms_url_ready = terms_url_ready[:-3]
    query_url = query_url + query_str
    html_doc = requests.get(query_url).content
    soup = BeautifulSoup(html_doc, 'html.parser')
    for link in soup.find_all('a', href=True):
        link_i = link.get('href')
        if (((link_i[0:len_url_start]) == ALL_REC_URL_START) and
            ((link_i[len_url_start:(len_sub_url+len_url_start)]) ==
             URL_REC_SUB_TARGET)):
            link_lst.append(link.get('href'))
    second_p_url = second_p_url + terms_url_ready
    second_p_url = second_p_url + '='
    second_p_url = second_p_url + terms_url_ready
    second_p_url = second_p_url + '&offset='
    subsequent_url_base = second_p_url
    y = 0
    while True:
        offset = (y * 24) + 24
        y = y + 1
        temp_url = subsequent_url_base + str(offset)
        temp_url = temp_url + '&q='
        temp_url = temp_url + terms_url_ready
        res_lst = search_later_pages(temp_url)
        if len(res_lst) == 0:
            break
        for x in range(len(res_lst)):
            link_lst.append(res_lst[x])
    return link_lst


def split_search_query_inc_exc(search_query):
    search_split = ((unquote(search_query)).strip()).split(';:;')
    search_term = ''
    inclusions = ''
    exclusions = ''
    inclusions_list = []
    exclusions_list = []
    if len(search_split) == 0:
        print("No Search Term")
        abort(400, 'No Search Term', custom='000001')
    if len(search_split) == 1:
        if len((unquote(search_split[0])).strip()) > 0:
            print("Search Term Only, No Include/Exclude")
            search_term = unquote(search_split[0]).strip()
        else:
            print("No Search Term")
            abort(400, 'No Search Term', custom='000002')
        # print(search_term)
    elif len(search_split) == 2:
        print("Search Term and Include Only, No Exclude")
        search_term = unquote(search_split[0]).strip()
        inclusions = unquote(search_split[1]).strip()
    elif len(search_split) == 3:
        print("Search Term, Include AND Exclude")
        search_term = unquote(search_split[0]).strip()
        inclusions = unquote(search_split[1]).strip()
        exclusions = unquote(search_split[2]).strip()
    if inclusions != '':
        inclusions_list = inclusions.split(',')
    if exclusions != '':
        exclusions_list = exclusions.split(',')
    # Return
    return_dict = {"search_term": search_term,
                   "inclusions": inclusions_list,
                   "exclusions": exclusions_list}
    return return_dict


@api.route('/hello')
class HelloWorld(Resource):
    """
    The purpose of the HelloWorld class is to have a simple test to see if the
    app is working at all.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    def get(self):
        """
        A trivial endpoint to see if the server is running.
        It just answers with "hello world."
        """
        return {MESSAGE: 'hello world'}


# reconfigure for react
@api.route('/searchUISettings')
class GetSettings(Resource):
    """
    This endpoint gets current
    search and UI settings.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    def get(self):
        """
        This endpoint gets current
        search and UI settings.
        """
        return {'Data': {'BACKGROUND': 'DARK/LIGHT', 'Font': 'Standard'},
                'Type': {'Data': 2},
                'Title': {'UI Settings': 'Example Setting'}}


@recipes.route('/dbtest')
class DbTest(Resource):
    """
    Endpoint to test the data getting from the database
    in the /db/db.py file
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    def get(self):
        """
        Endpoint that Searches the DB for Armenian Pizza (Lahmahjoon)
        and Returns Recipe Details
        """
        return recmongo.get_recipe_details("Armenian Pizzas (Lahmahjoon)")


@recipes.route('/deleteSavedRecipe/<recipe_name>')
class DeleteSavedRecipe(Resource):
    """
    Deletes a saved recipe from the db based on name
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    def delete(self, recipe_name):
        """
        Deletes a recipe from the DB based on
        Recipe Name
        """
        return recmongo.delete_recipe_by_name(recipe_name)


@recipes.route('/filterByCalories')
class FilterByCalories(Resource):
    """
    This endpoint will allow you to filter by calories for all
    the recipes.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    def get(self):
        return {'Data': {"Cuisine": "Chinese",
                         "Food": "Roasted Pork",
                         "Drink": "Ginger Lime Ice Green Tea",
                         "Calories": "1003"},
                'Type': {'Data': 12},
                'Title': {'Suggestion': 'Chinese Food'}
                }


@recipes.route('/filterByDietType')
class FilterByDietType(Resource):
    """
    This endpoint will allow you to filter by specific diet types
    that people might fall under.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    def get(self):
        return {'Type': {'Vegetarian', 'Vegan', 'Pescatarian'}}


@recipes.route('/format')
class DataFormat(Resource):
    """
    This class serves to inform the user on the format of the db
    entries and also servers to assert that the entires are
    of the right form
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
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


@recipes.route('/getAllRecipes')
class GetAll(Resource):
    """
    This endpoint servers to return all recipes in the
    database and return them as a list of JSONs.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    def get(self):
        """
        Returns All Recipes From the DB
        """
        # return recdb.get_all()
        return recmongo.get_recipes_dict()


@recipes.route('/getRecipe/<recipe_name>')
class GetRecipe(Resource):
    """
    Gets a recipe from the db based on name
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    def get(self, recipe_name):
        """
        Gets a recipe from the db based on name
        """
        rec_name = (unquote(recipe_name)).strip()
        return recmongo.get_recipe_details(rec_name)


@recipes.route('/getRecipeFromURL/<path:website>')
class GetRecipeFromURL(Resource):
    """
    Gets a recipe from the db based URL
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    def get(self, website):
        """
        Gets a recipe form the DB based on URL
        """
        # rec_name = (unquote(website)).strip()
        # print('GetRecipeFromURL: ' + f'{rec_name=}')
        ret = recmongo.get_recipe_from_rec_url(website)
        # print('GetRecipeFromURL: ' + f'{ret=}')
        return ret


@recipes.route('/getRecipeSuggestions')
class GetRecipeSuggestions(Resource):
    """
    This endpoint serves to return a dictionary of
    recipe suggestions from the database.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    def get(self):
        return {'Data': {"Cuisine": "Chinese",
                         "Food": "Roasted Pork",
                         "Drink": "Ginger Lime Ice Green Tea"},
                'Type': {'Data': 12},
                'Title': {'Suggestion': 'Chinese Food'}
                }


@recipes.route('/list')
class List(Resource):
    """
    This will get a list of recipes.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    def get(self):
        return {RECIPES_LIST_NM: recmongo.get_recipes()}


@recipes.route('/loadDB')
class LoadDB(Resource):
    """
    DEVELOPER ENDPOINT
    This endpoint searches allrecipes.com for each of
    the search terms that are in the search_terms.txt
    file that is in /server . The endpoint takes each
    term and exhaustively searches allrecipes.com
    for each of them individually and loads all recipes
    into the DB
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    def get(self):
        """
        DEVELOPER ENDPOINT
        This endpoint searches allrecipes.com
        for each search term that is in search_terms.txt
        that is located in /server . The endpoint
        takes each term and exhaustively searches
        allrecipes.com for each of them individually and
        loads all recipes into the DB
        """
        print("LoadDB:		INSIDE LoadDB")
        print("LoadDB:		Loading Search Terms...")
        search_terms = load_search_terms(SEARCH_TERMS_FILE_NAME)
        print("LoadDB:		Search Terms Loaded!")
        for x in search_terms:
            print("LoadDB:		_______________")
            print("LoadDB:		Search Term: " + x)
            print("LoadDB:		Getting List of Recipe URL's...")
            url_list = search_all_rec_from_query(x)
            print("LoadDB:		URL's Gathered!")
            for y in url_list:
                html_doc = requests.get(y).content
                soup = BeautifulSoup(html_doc, 'html.parser')
                scrape_return = scrape_website_soup(soup, y)
                rec_to_ret_json = json.loads(json_util.dumps(scrape_return))
                rec_name = rec_to_ret_json["recipe_name"]
                print("LoadDB:		Recipe Name: " + rec_name)
                if (not (recmongo.recipe_exists_from_url(y))):
                    print("LoadDB:		Recipe not in DB, adding it...")
                    recmongo.add_recipe(rec_name, rec_to_ret_json)
                else:
                    print("LoadDB:		" + DB_MESSAGE_NOT)
        print("LoadDB:		LoadDB Completed Loading DB!!!")
        return True


@recipes.route(MAIN_MENU)
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


@recipes.route('/recipe_cuisines_list')
class RecipeCuisinesList(Resource):
    """
    This will get a list of recipe cuisines.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    def get(self):
        return {RECIPES_CUISINES_LIST_NM: recmongo.get_recipes()}


@recipes.route('/recipe_suggestions_list')
class RecipeSuggestionsList(Resource):
    """
    This will get a list of recipe suggestions.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    def get(self):
        return {RECIPES_SUGGESTIONS_LIST_NM: recmongo.get_recipes()}


@recipes.route(f'{SCRAPE_WEBSITE}/<path:website>')
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
        This endpoint will get html from the website and return
        a dictionary with the recipe info.
        This endpoint scrapes from allrecipes.com only
        """
        html_doc = requests.get(website).content
        soup = BeautifulSoup(html_doc, 'html.parser')
        scrape_return = scrape_website_soup(soup, website)
        rec_to_ret_json = json.loads(json_util.dumps(scrape_return))
        rec_name = rec_to_ret_json["recipe_name"]
        # print("inside ScrapeWebsite")
        # print("rec_name: " + rec_name)
        # Check if recipe is in db already based on URL
        # print(f'{rec_to_ret_json=}')
        # print(f'{rec_name=}')
        # print('before recipe_exists_from_url')
        # value = recmongo.recipe_exists_from_url(unquote(website))
        # print('after recipe_exists_from_url')
        # print(f'{value=}')
        if (not (recmongo.recipe_exists_from_url(website))):
            print("ScrapeWebsite: Recipe not in DB, adding it...")
            recmongo.add_recipe(rec_name, rec_to_ret_json)
        else:
            print("ScrapeWebsite: Recipe already in DB! NOT ADDING IT AGAIN!")
        # Recipe gets added to the database for later retrieval
        # recmongo.add_recipe(recipe_name, rec_to_ret_json)
        # print(rec_to_ret_json["url"])
        return rec_to_ret_json


@recipes.route('/searchAllRec/<search_query>')
class SearchAllRec(Resource):
    """
    This endpoint searches allrecipes.com for a given keyword and returns
    a list of url's to related pages
    example
    https://www.allrecipes.com/search?q=pesto+pizza
    second page example
    https://www.allrecipes.com/search?pizza=pizza&offset=24&q=pizza
    https://www.allrecipes.com/search?pesto%20pizza=pesto%20pizza&offset=24&q=pesto%20pizza
    third page example
    https://www.allrecipes.com/search?pizza=pizza&offset=48&q=pizza
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    def get(self, search_query):
        """
        This endpoint searches allrecipes.com
        for a given keyword and returns a list of
        url's to recipes related to search term
        """
        return search_all_rec_from_query(search_query)


@recipes.route('/searchFrontEnd/<search_query>')
class SearchFrontEnd(Resource):
    """
    This endpoint runs through a sequence of
    what we want our frontend to call.
    Once someone enters a search query with
    ingredients that they want to include
    or exclude, this endpoint will first
    pull all recipes associated with that
    search term and ensure they are in our DB
    next, we will search through the db for everything
    that matches that request.
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
        """
        This endpoint searches allrecipes.com
        for the search term and loads into the db
        then uses the inclusion and exclusion criteria
        to do a search of the db and returns the results
        Format for search will be as follows:
        'search term(s);:;inclusion1,inclusion2,
        inclusion3;:;exclusion1,exclusion2,exclusion3;:;'
        search with only inclusion:
        'search term(s);:;inclusion1,inclusion2,inclusion3'
        search with only exclusion:
        'search term(s);:;;:;exclusion1,exclusion2,
        exclusion3'
        search with only search term:
        'search term(s)'
        """
        # Process Search Query
        search_split_dict = split_search_query_inc_exc(search_query)
        # Split Return to Individual Parts
        search_term = search_split_dict["search_term"]
        inclusions_list = search_split_dict["inclusions"]
        exclusions_list = search_split_dict["exclusions"]
        # Get all recipes about the search term
        rec_url_list = search_all_rec_from_query(search_term)
        # Scrape each URL in list
        for x in rec_url_list:
            html_doc = requests.get(x).content
            soup = BeautifulSoup(html_doc, 'html.parser')
            scrape_return = scrape_website_soup(soup, x)
            url_data = json.loads(json_util.dumps(scrape_return))
            rec_name = url_data["recipe_name"]
            if (not (recmongo.recipe_exists_from_url(x))):
                print("Recipe not in DB, adding it...")
                # print(f'{url_data=}')
                recmongo.add_recipe(rec_name, url_data)
            else:
                print("recipe already in DB! NOT ADDING IT AGAIN!")
        # Search DB for Recipe with Inclusion and Exclusion
        results = recmongo.search_recipe_ingr(search_term, inclusions_list,
                                              exclusions_list)
        return results


@recipes.route(SEARCH_HATEOAS)
class SearchHateoas(Resource):
    """
    This Will return a menu list
    that the frontend can call to search
    for different recipes
    """
    def get(self):
        """
        Gets the search main menu.
        """
        return {'Title': SEARCH_HATEOAS_TITLE,
                'Default': 1,
                'Choices': {
                    '1': {'url': '/getAllRecipes', 'method': 'get',
                          'text': 'Get All Recipes'},
                    '2': {'url': f'{VEG_REC}', 'method': 'get',
                          'text': 'Get Vegetarian Recipes'},
                    '3': {'url': '/searchIncExc/;:;;:;soy', 'method': 'get',
                          'text': 'Get Recipes Without Soy'},
                    '4': {'url': '/searchIncExc/;:;;:;milk', 'method': 'get',
                          'text': 'Get Recipes Without Milk'},
                }}


@recipes.route('/searchIncExc/<search_query>')
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
        """
        Main Search Endpoint for Finding Recipes.
        This allows you to search with Ingredient
        Inclusions and Exclusions (though not required)
        Format for search will be as follows:
        'search term(s);:;inclusion1,inclusion2,
        inclusion3;:;exclusion1,exclusion2,exclusion3;:;'
        search with only inclusion:
        'search term(s);:;inclusion1,inclusion2,inclusion3'
        search with only exclusion:
        'search term(s);:;;:;exclusion1,exclusion2,
        exclusion3'
        search with only search term:
        'search term(s)'
        """
        # print(search_query)
        search_split_dict = split_search_query_inc_exc(search_query)
        search_term = search_split_dict["search_term"]
        inclusions_list = search_split_dict["inclusions"]
        exclusions_list = search_split_dict["exclusions"]
        results = recmongo.search_recipe_ingr(search_term, inclusions_list,
                                              exclusions_list)
        # for x in results:
        #     print(f'{type(x)=}')
        return results


@users.route('/add_saved_recipe')
class AddSavedRecipe(Resource):
    """
    Adds a recipe that the user wants to
    save to their own personal db
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    def post(self):
        """
        Adds a recipe to the DB based on
        Recipe ID
        """
        ret = {}
        username = request.form.get('username')
        logged_in = request.form.get('logged_in')
        session_token = request.form.get('session_token')
        recipe_id = request.form.get('recipe_id')
        username = text_strip(username)
        session_token = text_strip(session_token)
        recipe_id = text_strip(recipe_id)
        if isinstance(logged_in, int):
            if (logged_in == 0):
                logged_in = False
            elif (logged_in == 1):
                logged_in = True
            else:
                raise ValueError("logged_in is not an expected value")
        elif isinstance(logged_in, bool):
            pass
        else:
            raise ValueError("logged_in is not an expected type")
        ret["username"] = username
        ret["logged_in"] = logged_in
        ret["session_token"] = session_token
        ret["recipe_id"] = recipe_id
        if logged_in is False:
            ret["message"] = "User is not logged in. Can't add recipe"
            ret["success"] = 0
            return ret
        if not (usermongo.user_exists(username)):
            ret["message"] = "User does not Exist in the DB"
            ret["success"] = 0
            return ret
        if recipe_id == '':
            ret["message"] = "Recipe ID is blank!"
            ret["success"] = 0
        result = usermongo.add_saved_recipe(username, recipe_id)
        if result["success"] == 0:
            ret["message"] = result["message"]
            ret["success"] = result["success"]
            return ret
        # verify it was added
        user_details = usermongo.get_user_details(username)
        saved_recs = user_details[usermongo.SAVED_RECIPES]
        saved_recs_lst = saved_recs.split(';')
        checkval = False
        for x in saved_recs_lst:
            if x == recipe_id:
                checkval = True
        if checkval:
            ret["message"] = result["message"]
            ret["success"] = result["success"]
        return ret


@users.route('/add_saved_recipe_by_rec_name')
class AddSavedRecipeByRecName(Resource):
    """
    Adds a recipe that the user wants to
    save to their own personal db
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    def post(self):
        """
        Adds a recipe to the DB based on
        Recipe Name
        """
        ret = {}
        username = request.form.get('username')
        logged_in = request.form.get('logged_in')
        session_token = request.form.get('session_token')
        recipe_name = request.form.get('recipe_name')
        username = text_strip(username)
        session_token = text_strip(session_token)
        recipe_name = text_strip(recipe_name)
        if isinstance(logged_in, int):
            if logged_in == 0:
                logged_in = False
            elif logged_in == 1:
                logged_in = True
            else:
                raise ValueError("logged_in is not an expected value")
        elif isinstance(logged_in, bool):
            pass
        else:
            raise ValueError("logged_in is not an expected type")
        ret["username"] = username
        ret["logged_in"] = logged_in
        ret["session_token"] = session_token
        ret["recipe_name"] = recipe_name
        if logged_in is False:
            ret["message"] = "User is not logged in. Can't add recipe"
            ret["success"] = 0
            return ret
        if not (usermongo.user_exists(username)):
            ret["message"] = "User does not Exist in the DB"
            ret["success"] = 0
            return ret
        if recipe_name == '':
            ret["message"] = "Recipe Name is blank!"
            ret["success"] = 0
        rec = recmongo.get_recipe_details(recipe_name)
        rec_id = rec["_id"]["$oid"]
        result = usermongo.add_saved_recipe(username, rec_id)
        if result["success"] == 0:
            ret["message"] = result["message"]
            ret["success"] = result["success"]
            return ret
        # verify it was added
        user_details = usermongo.get_user_details(username)
        saved_recs = user_details[usermongo.SAVED_RECIPES]
        saved_recs_lst = saved_recs.split(';')
        checkval = False
        for x in saved_recs_lst:
            if x == rec_id:
                checkval = True
        if checkval:
            ret["message"] = result["message"]
            ret["success"] = result["success"]
        return ret


@users.route('/delete_user/<username>')
class DeleteUser(Resource):
    """
    This endpoint will be used to delete a user account
    from the DB.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    def get(self, username):
        """
        Delete a User
        """
        if usermongo.user_exists(username.strip()):
            return usermongo.delete_user(username.strip())
        else:
            return 0


# VERY VERY rudementary system put in place to allow us to test
# login before a working UI, this works with Swagger
@users.route('/login/<path:username>')  # /<path:password>')
class Login(Resource):
    """
    This is used as the login endpoint.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    def get(self, username):
        """
        The get() method
        Until we have a better system, the password will stay
        commented I guess :(
        """
        email_pattern = re.compile(
            r"[a-zA-Z0-9]+\.?[a-zA-Z0-9]+@[a-zA-Z]+\.(com|co|org|edu)"
        )
        if email_pattern.match(username):
            return {"username": username}  # , "password": password}
        return {"error": "username must be an email address"}


# This allows testing of the password storing and loging before
# having a workable UI
@users.route('/password/<path:password>')  # /<path:password>')
# @app.route('/password', methods=(['GET','POST']))
class Password(Resource):
    """
    This is used as the login endpoint.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    def get(self, password):
        """
        This takes the password and encrypts it and stores it
        """
        if not (65 > len(password) > 7):
            raise pswdError(len(password))

        # future improvement to display password strength here

        # encoded = password.encode('utf-8')
        # salt = bcrypt.gensalt()
        # hashed = bcrypt.hashpw(encoded, salt)
        hashed = hash_pwd(password)
        # return {"hashed": hashed.decode("utf-8")}
        return {"hashed": hashed}


@users.route('/register_user')
class RegisterUser(Resource):
    """
    This endpoint will be used to register for a user account.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    def post(self):
        """
        Registers a New User
        """
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        # email = request.form.get['email']
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        include_ingr_preference = request.form.get('inc_ingr_pref')
        exclude_ingr_preference = request.form.get('exc_ingr_pref')
        other_preferences = request.form.get('other_preferences')
        diet = request.form.get('diet')
        first_name = text_strip(first_name)
        last_name = text_strip(last_name)
        username = text_strip(username)
        password = text_strip(password)
        confirm_password = text_strip(confirm_password)
        include_ingr_preference = text_strip(include_ingr_preference)
        exclude_ingr_preference = text_strip(exclude_ingr_preference)
        other_preferences = text_strip(other_preferences)
        diet = text_strip(diet)
        user_data = {"first_name": first_name,
                     "last_name": last_name,
                     "username": username,
                     "inc_ingr_pref": include_ingr_preference,
                     "exc_ingr_pref": exclude_ingr_preference,
                     "other_preferences": other_preferences,
                     "diet": diet,
                     "saved_recipes": ''
                     }
        # first need to check if username already exists in database,
        # if so, return an error message saying that this user already exists
        # if not, add all of these fields into the MongoDB database
        # collection named "users" return a message stating that the
        # user was successfully registered!
        if username == '':
            user_data["message"] = "Username is Blank!!!"
            user_data["success"] = 0
            return user_data
        if usermongo.user_exists(username):
            # raise ValueError(f'Username: "{username=}" already exists')
            user_data["message"] = "Username Already Exists in DB"
            user_data["success"] = 0
            return user_data
        else:
            if password == confirm_password:
                hashed = hash_pwd(password)
                user_data["hashed_password"] = hashed
                usermongo.add_user(username, user_data)
                if usermongo.user_exists(username):
                    user_data["message"] = "User Added Successfully"
                    user_data["success"] = 1
                    return user_data
                else:
                    user_data["message"] = "Error Adding User to Database"
                    user_data["success"] = 0
                    return user_data
            else:
                user_data["message"] = "Passwords Don't Match"
                user_data["success"] = 0
                return user_data


@users.route('/update_password')
class UpdatePassword(Resource):
    """
    This endpoint will be used to update a user's password.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    def post(self):
        """
        update's a user's password
        """
        username = request.form.get('username')
        old_password = request.form.get('old_password')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        username = text_strip(username)
        old_password = text_strip(old_password)
        password = text_strip(password)
        confirm_password = text_strip(confirm_password)
        user_data = {}
        user_data_results = {}
        user_data["username"] = username
        res_mes = "Something Went Wrong; Password Not Updated Successfully"
        if username == '':
            user_data["message"] = "Username is Blank!!!"
            user_data["success"] = 0
            return user_data
        if not usermongo.user_exists(username):
            # raise ValueError(f'Username: "{username=}" already exists')
            user_data["message"] = "Username Does NOT EXIST in DB"
            user_data["success"] = 0
            return user_data
        else:
            if password == confirm_password:
                user_data_results = usermongo.get_user_details(username)
                if old_password == '':
                    user_data["message"] = "Old Password is Blank!"
                    user_data["success"] = 0
                    return user_data
                hashed = hash_pwd(password)
                old_hashed = hash_pwd(old_password)
                print(f'{user_data_results["hashed_password"]=}')
                print(f'{old_hashed=}')
                # if (user_data_results["hashed_password"] == old_hashed):
                db_pw_hash = user_data_results["hashed_password"]
                db_pw_hash = db_pw_hash.encode('utf-8')
                old_pwd_encoded = old_password.encode('utf-8')
                if bcrypt.checkpw(old_pwd_encoded, db_pw_hash):
                    user_data["hashed_password"] = hashed
                    result = usermongo.update_user_password(username, hashed)
                    user_data_results = usermongo.get_user_details(username)
                    pass_upd_succ = result["success"]
                    # hash_match = (user_data_results[HSHD_PWD_KEY] == hashed)
                    db_pw_hash_2 = user_data_results[HSHD_PWD_KEY]
                    db_pw_hash_2 = db_pw_hash_2.encode('utf-8')
                    pwd_encoded = password.encode('utf-8')
                    hash_match = bcrypt.checkpw(pwd_encoded, db_pw_hash_2)
                    if hash_match and pass_upd_succ:
                        user_data["message"] = PASS_SUCCESS_MESSAGE
                        user_data["success"] = 1
                        return user_data
                    else:
                        user_data["message"] = res_mes
                        user_data["success"] = 0
                        return user_data
                else:
                    user_data["message"] = INCORRECT_OLD_PWD
                    user_data["success"] = 0
                    return user_data
            else:
                user_data["message"] = "Passwords Don't Match"
                user_data["success"] = 0
                return user_data
