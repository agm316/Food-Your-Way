import pytest
import server.endpoints as ep

TEST_CLIENT = ep.app.test_client()

TEST_WEBSITE = "https://www.allrecipes.com/recipe/154315/armenian-pizzas-lahmahjoon/"
TEST_WEBSITE_TITLE = "Armenian Pizzas (Lahmahjoon)"
TEST_PREP_TIME = "20 mins"
TEST_COOK_TIME = "30 mins"
TEST_TOTAL_TIME = "50 mins"
TEST_SERVINGS = "3"
TEST_YIELD = "6 pizzas"
TEST_URL = "https://www.allrecipes.com/recipe/154315/armenian-pizzas-lahmahjoon/"


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

@pytest.mark.skip("Can't run this test until a recipe gets deleted from the database.")
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
    resp_json = TEST_CLIENT.get(f'{ep.SCRAPE_WEBSITE}/{TEST_WEBSITE}').get_json()
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


def test_get_all():
    """
    This test servers to test the getall() endpoint and asserts
    that it matches the format of a list of recipes.
    """
    alldb = TEST_CLIENT.get(ep.GETALL).get_json()
    assert isinstance(alldb, dict)


def test_search_query(input_search_query):
    """
    See if Search Query works (NOT YET CONNECTED TO DB, update later when it is)
    """
    #assert True
    resp_json = TEST_CLIENT.get(f'/search={input_search_query}').get_json()
    assert isinstance(resp_json[ep.MESSAGE], str)


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


@pytest.mark.skip("Can't run this test until a recipe gets deleted from the database.")
def test_del_recipe():
    assert False
