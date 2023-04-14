import pytest
import json
import bson.json_util as json_util
from urllib.parse import unquote
import server.endpoints as ep
import db.recipes as recmongo
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


SEARCH_INC_EXC_TEST_QUERY = "soup;:;pumpkin,tomato;:;poop,soy"

RECIPE_DB = 'api_dev_db'

# {recipe_name: 'Armenian Pizzas (Lahmahjoon)'}

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


def test_delete_recipe_by_name():
    """
    Delete Armenian Pizza Recipe if it
    is in the DB
    """
    print('test_delete_recipe_by_name: Checking if Armenian Pizza is in DB...')
    if (not (recmongo.recipe_exists(TEST_WEBSITE_TITLE))):
        print('test_delete_recipe_by_name: RECIPE NOT IN DB')
        print('test_delete_recipe_by_name: SCRAPING URL TO ADD IT...')
        resp = TEST_CLIENT.get(f'/scrape/{TEST_WEBSITE}')
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
    assert TEST_CLIENT.get(f'/deleteRecipe/{TEST_WEBSITE_TITLE}')
    

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
    resp = TEST_CLIENT.get(f'/scrape/{TEST_WEBSITE}')
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
    resp = TEST_CLIENT.get(f'/scrape/{TEST_WEBSITE}')
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


# NOTE: Currently fails.  Can test author take a look?
# def test_get_database():
#
#     """
#     Test to see if data is being stored in the database the right
#     way and if the get data from the database works.
#     """
#     dbentry = TEST_CLIENT.get(ep.DBGETTEST).get_json()
#     assert dbentry["recipe_name"] == TEST_WEBSITE_TITLE
#     assert isinstance(dbentry["prep_time"], str)
#     assert isinstance(dbentry["cook_time"], str)
#     assert isinstance(dbentry["total_time"], str)
#     assert isinstance(dbentry["servings"], str)
#     assert isinstance(dbentry["ingredients"], str)
#     assert isinstance(dbentry["directions"], str)
#     assert isinstance(dbentry["rating"], str)
#     assert isinstance(dbentry["url"], str)
#     assert isinstance(dbentry, dict)


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
    resp_json = TEST_CLIENT.get(f'/searchIncExc/{SEARCH_INC_EXC_TEST_QUERY}').data
    # Need to fix this to be json dictionary and not bytes!!!
    assert isinstance(resp_json, bytes)


def test_search_query(input_search_query):
    """
    See if Search Query works
    """
    # assert True
    resp_json = TEST_CLIENT.get(f'/searchIncExc/{input_search_query}').get_json()
    # print(f'{type(resp_json)=}')
    assert isinstance(resp_json, list)


def test_get_recipe_cuisines_list():
    """
    This test will test the recipe cuisines namespace endpoint.
    """
    resp_json = TEST_CLIENT.get(ep.RECIPE_CUISINES_LIST_W_NS).get_json()
    assert isinstance(resp_json[ep.RECIPE_CUISINES_LIST_NM], list)


def test_get_recipe_suggestions_list():
    """
    This test will test the recipe suggestions namespace endpoint.
    """
    resp_json = TEST_CLIENT.get(ep.RECIPE_SUGGESTIONS_LIST_W_NS).get_json()
    assert isinstance(resp_json[ep.RECIPE_SUGGESTIONS_LIST_NM], list)


# @pytest.mark.skip("Unable to test this fully without UI")
def test_user_name():
    user = TEST_CLIENT.get(f"/login/{TEST_USER}").get_json()
    assert isinstance(user, dict)
    assert isinstance(user["username"], str)
    assert user["username"] == TEST_USER
    # assert isinstance(user["pwd"], str)


def test_user_name_fail():
    user = TEST_CLIENT.get(f"/login/{TEST_USER_FAIL}").get_json()
    assert isinstance(user, dict)
    assert isinstance(user["error"], str)
    assert user["error"] == "username must be an email address"
    # assert isinstance(user["pwd"], str)


def test_password():
    user = TEST_CLIENT.get(f"/password/{TEST_PSW}").get_json()
    assert isinstance(user, dict)
    assert isinstance(user["hashed"], str)
    assert len(user["hashed"]) > len(TEST_PSW)


def test_password_fail():
    response1 = TEST_CLIENT.get(f"/password/{TEST_FAIL_PSW_1}").get_json()
    assert(response1["message"] == 'Internal Server Error')
    response2 = TEST_CLIENT.get(f"/password/{TEST_FAIL_PSW_2}").get_json()
    assert(response2["message"] == 'Internal Server Error')
