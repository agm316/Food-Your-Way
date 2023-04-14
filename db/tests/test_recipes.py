"""
This file will test our recipes db file recipes.py
"""
import os
import pytest
import db.recipes as rec

RUNNING_ON_CICD_SERVER = os.environ.get('CI', False)

TEST_DEL_NAME = 'Recipe to be deleted'


def create_recipe_details():
    details = {}
    for field in rec.REQUIRED_FIELDS:
        details[field] = 2
    return details


@pytest.fixture(scope='function')
def temp_recipe():
    rec.add_recipe(rec.TEST_RECIPE_NAME, create_recipe_details())
    yield
    rec.delete_recipe_by_name(rec.TEST_RECIPE_NAME)


@pytest.fixture(scope='function')
def new_recipe():
    return rec.add_recipe(TEST_DEL_NAME, create_recipe_details())


def test_del_recipe(new_recipe):
    rec.delete_recipe_by_name(TEST_DEL_NAME)
    assert not rec.recipe_exists(TEST_DEL_NAME)


def test_get_recipes(temp_recipe):
    recs = rec.get_recipes()
    assert isinstance(recs, list)
    assert len(recs) > 0


def test_get_recipes_dict(temp_recipe):
    recs = rec.get_recipes_dict()
    assert isinstance(recs, dict)
    assert len(recs) > 0


def test_get_recipe_details(temp_recipe):
    rec_dtls = rec.get_recipe_details(rec.TEST_RECIPE_NAME)
    assert isinstance(rec_dtls, dict)


def test_recipe_exists(temp_recipe):
    assert rec.recipe_exists(rec.TEST_RECIPE_NAME)


def test_recipe_not_exists():
    assert not rec.recipe_exists('Surely this is not a recipe name!')


def test_add_wrong_name_type():
    with pytest.raises(TypeError):
        rec.add_recipe(4, {})


def test_add_wrong_details_type():
    with pytest.raises(TypeError):
        rec.add_recipe('a new recipe', [])


def test_add_missing_field():
    with pytest.raises(ValueError):
        rec.add_recipe('a new recipe', {'bla': 'bla'})


def test_add_recipe():
    rec.add_recipe(rec.TEST_RECIPE_NAME, create_recipe_details())
    assert rec.recipe_exists(rec.TEST_RECIPE_NAME)
    rec.delete_recipe_by_name(rec.TEST_RECIPE_NAME)