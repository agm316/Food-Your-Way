import pytest
import server.endpoints as ep

TEST_CLIENT = ep.app.test_client()

TEST_WEBSITE = "https://www.allrecipes.com/recipe/154315/armenian-pizzas-lahmahjoon/"
TEST_WEBSITE_TITLE = "Armenian Pizzas (Lahmahjoon)"

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
    assert isinstance(resp_json["ingredients"], str)
    assert isinstance(resp_json["directions"], str)
    assert isinstance(resp_json["rating"], str)
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
    assert isinstance(dbformat["name"], str)

# Database is currently not working, trying to get a resolution
# def test_get_database():
#
#     """
#     Test to see if data is being stored in the database the right
#     way and if the get data from the database works.
#     """
#     dbentry = TEST_CLIENT.get(ep.DBGETTEST).get_json()
#     assert ((dbentry["recipe_name"]) == (TEST_WEBSITE_TITLE))
#     assert isinstance(dbentry["ingredients"], str)
#     assert isinstance(dbentry["directions"], str)
#     assert isinstance(dbentry["rating"], str)
#     assert isinstance(dbentry, dict)