"""
This is the file containing all the endpoints for our flask app.
The endpoint called `endpoints` will return all available endpoints.
"""

# import time
# import urllib3
from bs4 import BeautifulSoup
from flask import Flask, request
from flask_restx import Resource, Api, Namespace, abort
from http import HTTPStatus
from pymongo import MongoClient
from db import db as recdb  # need to fix issue with make prod
from db import recipes as recmongo
from urllib.parse import unquote
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
ALL_REC_URL_START = 'https://www.allrecipes.com/'
URL_REC_SUB_TARGET = 'recipe/'
SEARCH_HATEOAS = '/search_hateoas'
SEARCH_HATEOAS_TITLE = 'Recipe Options'
VEG_REC = '/searchIncExc/Vegetarian;:;;:;'

recipe_cuisines = Namespace(RECIPE_CUISINES_NS, 'Recipe Cuisines')
api.add_namespace(recipe_cuisines)

recipe_suggestions = Namespace(RECIPE_SUGGESTIONS_NS, 'Recipe Suggestions')
api.add_namespace(recipe_suggestions)


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
    if (not isinstance(nutr_soup, type(None))):
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
    elif (isinstance(img2_soup, type(None))):
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
    if (len(term_lst) == 0):
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
    while (True):
        offset = (y * 24) + 24
        y = y + 1
        temp_url = subsequent_url_base + str(offset)
        temp_url = temp_url + '&q='
        temp_url = temp_url + terms_url_ready
        res_lst = search_later_pages(temp_url)
        if (len(res_lst) == 0):
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
    if (len(search_split) == 0):
        print("No Search Term")
        abort(400, 'No Search Term', custom='000001')
    if (len(search_split) == 1):
        if (len((unquote(search_split[0])).strip()) > 0):
            print("Search Term Only, No Include/Exclude")
            search_term = unquote(search_split[0]).strip()
        else:
            print("No Search Term")
            abort(400, 'No Search Term', custom='000002')
        # print(search_term)
    elif (len(search_split) == 2):
        print("Search Term and Include Only, No Exclude")
        search_term = unquote(search_split[0]).strip()
        inclusions = unquote(search_split[1]).strip()
    elif (len(search_split) == 3):
        print("Search Term, Include AND Exclude")
        search_term = unquote(search_split[0]).strip()
        inclusions = unquote(search_split[1]).strip()
        exclusions = unquote(search_split[2]).strip()
    if (inclusions != ''):
        inclusions_list = inclusions.split(',')
    if (exclusions != ''):
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


@api.route('/register_user')
class Register_User(Resource):
    """
    This endpoint will be used to register for an account.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    def post(self):
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # first need to check if username already exists in database,
        # if so, return an error message saying that this user already exists
        # if not, add all of these fields into the MongoDB database
        # collection named "users" return a message stating that the
        # user was successfully registered!
        return {"First Name": first_name, "Last Name": last_name,
                "Email": email, "Username": username,
                "Password": password, "Confirm Password":
                    confirm_password}


# VERY VERY rudementary system put in place to allow us to test
# login before a working UI, this works with Swagger
@api.route('/login/<path:username>')  # /<path:password>')
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
@api.route('/password/<path:password>')  # /<path:password>')
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


@api.route('/getRecipeSuggestions')
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
        return {'Data': {'BACKGROUND': 'DARK/LIGHT', 'Font': 'Standard'},
                'Type': {'Data': 2},
                'Title': {'UI Settings': 'Example Setting'}}


@api.route('/getAllRecipes')
class GetAll(Resource):
    """
    This endpoint servers to return all recipes in the
    database and return them as a list of JSONs.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
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
        # print(search_query)
        search_split_dict = split_search_query_inc_exc(search_query)
        search_term = search_split_dict["search_term"]
        inclusions_list = search_split_dict["inclusions"]
        exclusions_list = search_split_dict["exclusions"]
        results = recmongo.search_recipe_ingr(search_term, inclusions_list,
                                              exclusions_list)
        return results


@api.route('/searchAllRec/<search_query>')
class SearchAllRec(Resource):
    """
    This endpoint searches allrecipes.com for a given keyword and returns
    a list of url's to related pages
    so far this only returns one page
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
        return search_all_rec_from_query(search_query)


@api.route('/searchFrontEnd/<search_query>')
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


@api.route('/deleteRecipe/<recipe_name>')
class DeleteRecipe(Resource):
    """
    deletes a recipe from the db based on name
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    def get(self, recipe_name):
        return recmongo.delete_recipe_by_name(recipe_name)


@api.route('/getRecipe/<recipe_name>')
class GetRecipe(Resource):
    """
    deletes a recipe from the db based on name
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    def get(self, recipe_name):
        rec_name = (unquote(recipe_name)).strip()
        return recmongo.get_recipe_details(rec_name)


@api.route('/getRecipeFromURL/<path:website>')
class GetRecipeFromURL(Resource):
    """
    deletes a recipe from the db based on name
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    def get(self, website):
        # rec_name = (unquote(website)).strip()
        # print('GetRecipeFromURL: ' + f'{rec_name=}')
        ret = recmongo.get_recipe_from_rec_url(website)
        # print('GetRecipeFromURL: ' + f'{ret=}')
        return ret


@api.route('/filterByCalories')
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


@api.route(SEARCH_HATEOAS)
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
                    '1': {'url': f'/{GET_ALL_RECIPES}', 'method': 'get',
                          'text': 'Get All Recipes'},
                    '2': {'url': f'{VEG_REC}', 'method': 'get',
                          'text': 'Get Vegetarian Recipes'},
                    '3': {'url': '/searchIncExc/;:;;:;soy', 'method': 'get',
                          'text': 'Get Recipes Without Soy'},
                    '4': {'url': '/searchIncExc/;:;;:;milk', 'method': 'get',
                          'text': 'Get Recipes Without Milk'},
                }}


@api.route('/filterByDietType')
class FilterByDietType(Resource):
    """
    This endpoint will allow you to filter by specific diet types
    that people might fall under.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    def get(self):
        return {'Type': {'Vegetarian', 'Vegan', 'Pescatarian'}}


@api.route('/dbtest')
class DbTest(Resource):
    """
    Endpoint to test the data getting from the database
    in the /db/db.py file
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    def get(self):
        return recmongo.get_recipe_details("Armenian Pizzas (Lahmahjoon)")


@recipe_cuisines.route(RECIPE_CUISINES_LIST)
class RecipeCuisinesList(Resource):
    """
    This will get a list of recipe cuisines.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    def get(self):
        return {RECIPE_CUISINES_LIST_NM: recdb.get_all()}


@recipe_suggestions.route(RECIPE_SUGGESTIONS_LIST)
class RecipeSuggestionsList(Resource):
    """
    This will get a list of recipe suggestions.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    def get(self):
        return {RECIPE_SUGGESTIONS_LIST_NM: recdb.get_all()}


# adding in a basic hashing algorithm for a user's password
# will add to this when working with the login system
def md5(user_password):
    result = hashlib.md5(user_password.encode())
    return result.hexdigest()
