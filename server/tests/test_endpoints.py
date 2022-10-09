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
    assert isinstance(resp_json, dict)