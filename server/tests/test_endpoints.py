import pytest
import server.endpoints as ep

TEST_CLIENT = ep.app.test_client()

TEST_WEBSITE = "https://www.allrecipes.com/recipe/154315/armenian-pizzas-lahmahjoon/"
TEST_WEBSITE_TITLE = "Armenian Pizzas (Lahmahjoon)"

TEST_SEARCH_QUERY = "Pizza"

def test_hello():
    """
    See if Hello works
    """
    #assert True
    resp_json = TEST_CLIENT.get(ep.HELLO).get_json()
    assert isinstance(resp_json[ep.MESSAGE], str)


def test_scrape_website():
    """
    Test the web scraping endpoint
    checks a specific 'test' website and checks if the title matches
    what we know it should be, it also checks that ingredients is a 
    string and the whole return is a dictionary
    """
    resp_json = TEST_CLIENT.get(f'{ep.SCRAPE_WEBSITE}/{TEST_WEBSITE}').get_json()
    assert ((resp_json["recipe_name"]) == (TEST_WEBSITE_TITLE))
    assert isinstance(resp_json["prep_time"], str)
    assert isinstance(resp_json["cook_time"], str)
    assert isinstance(resp_json["total_time"], str)
    assert isinstance(resp_json["servings"], str)
    assert isinstance(resp_json["ingredients"], str)
    assert isinstance(resp_json["directions"], str)
    assert isinstance(resp_json["rating"], str)
    assert isinstance(resp_json["url"], str)
    assert isinstance(resp_json["nutrition"], str)
    assert isinstance(resp_json["timing"], str)
    assert isinstance(resp_json["cuisine_path"], str)
    assert isinstance(resp_json["img_src"], str)
    assert isinstance(resp_json, dict)

def test_format_endpoint():

    """
    This endpoint is used to test the format that we 
    advertise matches the format that is returned from the
    endpoints.
    TEST IS PURELY DONE IN AN EXAMPLERY WAY AT THE MOMENT
    will update with more rigorous test later on.
    """

    dbformat = TEST_CLIENT.get(ep.FORMAT).get_json()
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


def test_get_database():

    """
    Test to see if data is being stored in the database the right
    way and if the get data from the database works.
    """
    dbentry = TEST_CLIENT.get(ep.DBGETTEST).get_json()
    assert ((dbentry["recipe_name"]) == (TEST_WEBSITE_TITLE))
    assert isinstance(dbentry["prep_time"], str)
    assert isinstance(dbentry["cook_time"], str)
    assert isinstance(dbentry["total_time"], str)
    assert isinstance(dbentry["servings"], str)
    assert isinstance(dbentry["ingredients"], str)
    assert isinstance(dbentry["directions"], str)
    assert isinstance(dbentry["rating"], str)
    assert isinstance(dbentry["url"], str)
    assert isinstance(dbentry, dict)


def test_get_all():
    """
    This test servers to test the getall() endpoint and asserts
    that it matches the format of a list of recipes.
    """
    alldb = TEST_CLIENT.get(ep.GETALL).get_json()
    assert isinstance(alldb, list)



def test_search_query():
    """
    See if Search Query works (NOT YET CONNECTED TO DB, update later when it is)
    """
    #assert True
    resp_json = TEST_CLIENT.get(f'/search={TEST_SEARCH_QUERY}').get_json()
    assert isinstance(resp_json[ep.MESSAGE], str)

def test_get_recipe_cuisines_list():
    """
    This test will test the recipe cuisines namespace endpoint.
    """
    resp_json = TEST_CLIENT.get(ep.RECIPE_CUISINES_LIST_W_NS).get_json()
    assert isinstance(resp_json[ep.RECIPE_CUISINES_LIST_NM], list)
