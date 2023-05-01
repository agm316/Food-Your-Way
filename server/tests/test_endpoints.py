import pytest
from unittest.mock import patch
from http import HTTPStatus
import json
import bson.json_util as json_util
from urllib.parse import unquote
import server.endpoints as ep
import db.recipes as recmongo
import db.users as usermongo
from ..errs import pswdError

TEST_CLIENT = ep.app.test_client()

TEST_WEBSITE = "https://www.allrecipes.com/recipe/154315/armenian-pizzas-lahmahjoon/"
TEST_WEBSITE_TITLE = "Armenian Pizzas (Lahmahjoon)"
TEST_PREP_TIME = "20 mins"
TEST_COOK_TIME = "30 mins"
TEST_TOTAL_TIME = "50 mins"
TEST_SERVINGS = "3"
TEST_YIELD = "6 pizzas"
TEST_URL = "https://www.allrecipes.com/recipe/154315/armenian-pizzas-lahmahjoon/"

TEST_USER = "username.user@gmail.com"
TEST_USER_FAIL = "test"
TEST_PSW = "password"

TEST_FAIL_PSW_1 = "psswd"
# This tests max pswed length (has to be long)
TEST_FAIL_PSW_2 = "12345678901234567890123456789012345678901234567890123456789012345"

SAMPLE_RECIPE_DETAILS = {'_id': {'$oid': '64231fd4502eab40303bfde4'}, 'recipe_name': 'Armenian Pizzas (Lahmahjoon)', 'prep_time': '20 mins', 'cook_time': '30 mins', 'total_time': '50 mins', 'servings': '3', 'yield': '6 pizzas', 'ingredients': '1 pound lean ground lamb, ½ teaspoon salt, ¼ teaspoon ground black pepper, 1 tablespoon extra-virgin olive oil, ½ cup chopped red onion, 3 cloves garlic, minced, ½  green bell pepper, chopped, 1 tablespoon freshly ground cumin seed, 1 teaspoon ground turmeric, 1 teaspoon paprika, 1 pinch fenugreek seeds, finely crushed (Optional), 1  lemon wedge, 1 (14.5 ounce) can diced tomatoes, 2 tablespoons ketchup, 1 cup chopped flat-leaf parsley, 6 (6 inch) pita bread rounds, ⅓ cup crumbled feta cheese (Optional), 1  lime, cut into wedges, 1 tablespoon chopped fresh mint', 'directions': 'Preheat oven to 450 degrees F (230 degrees C). Season lamb with salt and pepper, and set aside.\nHeat olive oil in large skillet over medium-high heat. Add onion, garlic, and bell pepper and stir until just beginning to brown. Stir in the cumin, turmeric, paprika, and fenugreek.\nImmediately add the ground lamb. Squeeze lemon wedge over lamb, and drop the peel into the mixture. Break up the meat and stir until it has browned. Remove lemon peel.\nStir in the tomatoes, ketchup, and parsley. Continue to simmer until most of the liquid has evaporated, 10 to 15 minutes. The mixture should be spreadable but not too wet or the pitas will become soggy.\nArrange pitas on a large baking sheet unless you are baking them directly on the oven rack. Spoon meat mixture onto pitas and smooth into an even layer to within 1/8 inch of the edge of the pita. Sprinkle feta cheese on the meat mixture.\nBake pitas until the edges are slightly crisp and meat is lightly browned but not dried out, about 10 to 20 minutes depending on whether pitas are on a baking sheet or on the oven rack. Squeeze lime lightly over the top, sprinkle with chopped mint and enjoy!', 'rating': '4.5', 'url': 'https://www.allrecipes.com/recipe/154315/armenian-pizzas-lahmahjoon/', 'cuisine_path': '/Meat and Poultry/Lamb/Ground/', 'nutrition': 'Total Fat 33g 42%, Saturated Fat 14g 68%, Cholesterol 126mg 42%, Sodium 1663mg 72%, Total Carbohydrate 75g 27%, Dietary Fiber 7g 23%, Total Sugars 11g, Protein 42g, Vitamin C 68mg 342%, Calcium 369mg 28%, Iron 11mg 63%, Potassium 1003mg 21%', 'timing': 'Prep Time: 20 mins, Cook Time: 30 mins, Total Time: 50 mins, Servings: 3, Yield: 6 pizzas', 'img_src': 'https://www.allrecipes.com/thmb/4cLLHor7cXeVg9rds4vs3Q9yt0U=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/211614-c6da8451a13b464980f7feb8d4eb9c02.jpg'}
CRAZY_SEARCH = 'toenails test recipe;:;poop;:;'

SEARCH_INC_EXC_TEST_QUERY = "soup;:;pumpkin,tomato;:;poop,soy"

RECIPE_DB = 'api_dev_db'

TEST_USER_REGISTRATION_DATA = {"first_name": "TEST FIRST",
                               "last_name": "TEST LAST",
                               "username": "user@name.com",
                               "inc_ingr_pref": "",
                               "exc_ingr_pref": "",
                               "other_preferences": "",
                               "diet": "",
                               "saved_recipes": '',
                               "password": 'abcdefghij',
                               "confirm_password": 'abcdefghij'}
TEST_USER_UPDATE_PWD = {"username": "user@name.com",
                        "old_password": 'abcdefghij',
                        "password": 'newpassword',
                        "confirm_password": 'newpassword'}


# replaces TEST_SEARCH_QUERY
@pytest.fixture
def input_search_query():
    ret = "Pizza"
    return ret


# replaces TEST_CLIENT
@pytest.fixture
def input_test_client():
    ret = ep.app.test_client()
    return ret


def test_hello(input_test_client):
    """
    See if Hello works
    """
    # assert True
    resp_json = input_test_client.get(ep.HELLO).get_json()
    assert isinstance(resp_json[ep.MESSAGE], str)


def test_get_recipes_list():
    """
    This test will test the recipes namespace endpoint.
    """
    resp_json = TEST_CLIENT.get(ep.RECIPES_LIST_W_NS).get_json()
    assert isinstance(resp_json[ep.RECIPES_LIST_NM], list)


def test_delete_recipe_by_name():
    """
    Delete Armenian Pizza Recipe if it
    is in the DB
    """
    print('test_delete_recipe_by_name: Checking if Armenian Pizza is in DB...')
    if not (recmongo.recipe_exists(TEST_WEBSITE_TITLE)):
        print('test_delete_recipe_by_name: RECIPE NOT IN DB')
        print('test_delete_recipe_by_name: SCRAPING URL TO ADD IT...')
        resp = TEST_CLIENT.get(f'/recipes/scrape/{TEST_WEBSITE}')
        print('test_delete_recipe_by_name: CHECKING IF RECIPE IS IN DB NOW...')
        if recmongo.recipe_exists(TEST_WEBSITE_TITLE):
            print("test_delete_recipe_by_name: IT'S THERE!!!")
        else:
            print('test_delete_recipe_by_name: RECIPE NOT IN DB AGAIN?!?!?!')
            assert False
    else:
        print('test_delete_recipe_by_name: RECIPE EXISTS!!!')
    print('test_delete_recipe_by_name: TRYING TO DELETE Armenian Pizza Recipe...')
    # assert recmongo.delete_recipe_by_name(TEST_WEBSITE_TITLE)
    assert TEST_CLIENT.get(f'/recipes/deleteSavedRecipe/{TEST_WEBSITE_TITLE}')
    

def test_scrape_website():
    """
    Test the web scraping endpoint
    checks a specific 'test' website and checks if the title matches
    what we know it should be, it also checks that ingredients is a
    string and the whole return is a dictionary
    NOTE:
          If things here start to fail, then allrecipes
          could have changed their id tags for their website
          verify that the code in endpoints.py is using the
          correct id tags.
    """
    resp = TEST_CLIENT.get(f'/recipes/scrape/{TEST_WEBSITE}')
    resp2 = resp.get_json()
    resp_json = json.loads(json_util.dumps(resp2))
    # print(f'{type(resp)=}')
    # print(f'{resp2=}')
    # print(type(resp_json))
    # print(resp_json)
    assert isinstance(resp_json["recipe_name"], str)
    assert isinstance(resp_json["prep_time"], str)
    assert isinstance(resp_json["cook_time"], str)
    assert isinstance(resp_json["total_time"], str)
    assert isinstance(resp_json["servings"], str)
    assert isinstance(resp_json["yield"], str)
    assert isinstance(resp_json["ingredients"], str)
    assert isinstance(resp_json["directions"], str)
    assert isinstance(resp_json["rating"], str)
    assert isinstance(resp_json["url"], str)
    assert isinstance(resp_json["nutrition"], str)
    assert isinstance(resp_json["timing"], str)
    assert isinstance(resp_json["cuisine_path"], str)
    assert isinstance(resp_json["img_src"], str)
    assert isinstance(resp_json, dict)
    assert resp_json["recipe_name"] == TEST_WEBSITE_TITLE
    assert resp_json["prep_time"] == TEST_PREP_TIME
    assert resp_json["cook_time"] == TEST_COOK_TIME
    assert resp_json["total_time"] == TEST_TOTAL_TIME
    assert resp_json["servings"] == TEST_SERVINGS
    assert resp_json["yield"] == TEST_YIELD
    assert resp_json["url"] == TEST_URL


def test_recipe_exists():
    """
    Check to see if we can see if
    recipe that we added to db is in
    db now
    """
    assert recmongo.recipe_exists(TEST_WEBSITE_TITLE)


def test_scrape_website_already_in_db():
    """
    Check to see if we still are good
    scraping a website we already have
    in db
    """
    resp = TEST_CLIENT.get(f'/recipes/scrape/{TEST_WEBSITE}')
    resp2 = resp.get_json()
    resp_json = json.loads(json_util.dumps(resp2))
    assert isinstance(resp_json["recipe_name"], str)
    assert isinstance(resp_json["prep_time"], str)
    assert isinstance(resp_json["cook_time"], str)
    assert isinstance(resp_json["total_time"], str)
    assert isinstance(resp_json["servings"], str)
    assert isinstance(resp_json["yield"], str)
    assert isinstance(resp_json["ingredients"], str)
    assert isinstance(resp_json["directions"], str)
    assert isinstance(resp_json["rating"], str)
    assert isinstance(resp_json["url"], str)
    assert isinstance(resp_json["nutrition"], str)
    assert isinstance(resp_json["timing"], str)
    assert isinstance(resp_json["cuisine_path"], str)
    assert isinstance(resp_json["img_src"], str)
    assert isinstance(resp_json, dict)
    assert resp_json["recipe_name"] == TEST_WEBSITE_TITLE
    assert resp_json["prep_time"] == TEST_PREP_TIME
    assert resp_json["cook_time"] == TEST_COOK_TIME
    assert resp_json["total_time"] == TEST_TOTAL_TIME
    assert resp_json["servings"] == TEST_SERVINGS
    assert resp_json["yield"] == TEST_YIELD
    assert resp_json["url"] == TEST_URL


def test_format_endpoint(input_test_client):

    """
    This endpoint is used to test the format that we 
    advertise matches the format that is returned from the
    endpoints.
    TEST IS PURELY DONE IN AN EXAMPLERY WAY AT THE MOMENT
    will update with more rigorous test later on.
    """

    dbformat = input_test_client.get(ep.FORMAT).get_json()
    assert isinstance(dbformat, dict)
    assert isinstance(dbformat["row"], str)
    assert isinstance(dbformat["name"], str)
    assert isinstance(dbformat["prep_time"], str)
    assert isinstance(dbformat["cook_time"], str)
    assert isinstance(dbformat["total_time"], str)
    assert isinstance(dbformat["servings"], str)
    assert isinstance(dbformat["yield"], str)
    assert isinstance(dbformat["ingredients"], list)
    assert isinstance(dbformat["directions"], list)
    assert isinstance(dbformat["url"], str)


# @pytest.mark.skip("Can't run this test until a recipe gets deleted from the database.")
def test_get_all():
    """
    This test servers to test the getall() endpoint and asserts
    that it matches the format of a list of recipes.
    """
    alldb = TEST_CLIENT.get(ep.GETALL).get_json()
    assert isinstance(alldb, dict)


def test_search_inc_exc():
    """
    See if searchIncExc works
    """
    resp_json = TEST_CLIENT.get(f'/recipes/searchIncExc/{SEARCH_INC_EXC_TEST_QUERY}').get_json()
    # print(f'{type(resp_json)=}')
    # for x in resp_json:
    #     print(f'{type(x)=}')
    assert isinstance(resp_json, list)
    assert resp_json == []


@patch('db.recipes.search_recipe_ingr', return_value=SAMPLE_RECIPE_DETAILS)
def test_search_get_rec_details(mock_get_recipe_details):
    """
    See if we can search for
    Armenian Pizza
    """
    resp = TEST_CLIENT.get(f'/recipes/searchIncExc/{TEST_WEBSITE_TITLE};:;;:;')
    assert resp.status_code == HTTPStatus.OK
    resp_json = resp.get_json()
    assert resp_json['recipe_name'] == TEST_WEBSITE_TITLE


@patch('db.recipes.search_recipe_ingr', return_value=None)
def test_search_no_result(mock_get_recipe_details_none):
    """
    empty result for crazy search
    """
    resp = TEST_CLIENT.get(f'/recipes/searchIncExc/{CRAZY_SEARCH}')
    assert resp.status_code == HTTPStatus.OK
    resp_json = resp.get_json()
    assert resp_json is None


def test_search_query(input_search_query):
    """
    See if Search Query works
    """
    # assert True
    resp_json = TEST_CLIENT.get(f'/recipes/searchIncExc/{input_search_query}').get_json()
    # print(f'{type(resp_json)=}')
    assert isinstance(resp_json, list)


# @pytest.mark.skip("Unable to test this fully without UI")
def test_user_name():
    user = TEST_CLIENT.get(f"/users/login/{TEST_USER}").get_json()
    assert isinstance(user, dict)
    assert isinstance(user["username"], str)
    assert user["username"] == TEST_USER
    # assert isinstance(user["pwd"], str)


def test_user_name_fail():
    user = TEST_CLIENT.get(f"/users/login/{TEST_USER_FAIL}").get_json()
    assert isinstance(user, dict)
    assert isinstance(user["error"], str)
    assert user["error"] == "username must be an email address"
    # assert isinstance(user["pwd"], str)


def test_password():
    user = TEST_CLIENT.get(f"/users/password/{TEST_PSW}").get_json()
    assert isinstance(user, dict)
    assert isinstance(user["hashed"], str)
    assert len(user["hashed"]) > len(TEST_PSW)


def test_register_user():
    username = TEST_USER_REGISTRATION_DATA["username"]
    if usermongo.user_exists(username):
        print(f'test_endpoints.py:    test_register_user:{username=} exists')
        usermongo.delete_user(username)
        print(f'test_endpoints.py:    test_register_user:{username=} deleted')
    resp = TEST_CLIENT.post('/users/register_user', data=TEST_USER_REGISTRATION_DATA)
    resp1 = resp.get_json()
    print(f'test_endpoints.py:    resp1: {resp1=}')
    assert(resp1["success"] == 1)


def test_update_password():
    print(f'test_endpoints.py    test_update_password: Trying to update Password')
    username = TEST_USER_REGISTRATION_DATA["username"]
    resp = TEST_CLIENT.post('/users/update_password', data=TEST_USER_UPDATE_PWD)
    resp1 = resp.get_json()
    message = resp1["message"]
    success = resp1["success"]
    print(f'test_endpoints.py    test_update_password: RESULTS:')
    print(f'{message=}')
    print(f'{success=}')
    assert isinstance(resp1, dict)
    assert (success == 1)


def test_delete_user():
    resp = TEST_CLIENT.get(f'/users/delete_user/{TEST_USER_REGISTRATION_DATA["username"]}')
    resp_json = resp.get_json()
    assert(resp_json == 1)


def test_password_fail():
    response1 = TEST_CLIENT.get(f"/users/password/{TEST_FAIL_PSW_1}").get_json()
    assert(response1["message"] == 'Internal Server Error')
    response2 = TEST_CLIENT.get(f"/users/password/{TEST_FAIL_PSW_2}").get_json()
    assert(response2["message"] == 'Internal Server Error')
