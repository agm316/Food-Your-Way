"""
This file will test our users db file users.py
"""
import os
import pytest
import db.users as usr

RUNNING_ON_CICD_SERVER = os.environ.get('CI', False)

TEST_DEL_NAME = 'User to be deleted'
NEW_TEST_PASSWORD = 'NEW PASSWORD'
TEST_RECIPE_ID = '123456'


def create_user_details():
    details = {}
    for field in usr.REQUIRED_FIELDS:
        details[field] = '2'
    return details


@pytest.fixture(scope='function')
def temp_user():
    usr.add_user(usr.TEST_USER_NAME, create_user_details())
    yield
    usr.delete_user(usr.TEST_USER_NAME)


@pytest.fixture(scope='function')
def new_user():
    return usr.add_user(TEST_DEL_NAME, create_user_details())


def test_del_user(new_user):
    usr.delete_user(TEST_DEL_NAME)
    assert not usr.user_exists(TEST_DEL_NAME)


def test_get_user_details(temp_user):
    usr_dtls = usr.get_user_details(usr.TEST_USER_NAME)
    assert isinstance(usr_dtls, dict)


def test_user_exists(temp_user):
    assert usr.user_exists(usr.TEST_USER_NAME)


def test_user_not_exists():
    assert not usr.user_exists('Surely this is not a user name!')


def test_add_wrong_name_type():
    with pytest.raises(TypeError):
        usr.add_user(4, {})


def test_add_wrong_details_type():
    with pytest.raises(TypeError):
        usr.add_user('a new user', [])


def test_add_missing_field():
    with pytest.raises(ValueError):
        usr.add_user('a new user', {'bla': 'bla'})


def test_add_user():
    usr.add_user(usr.TEST_USER_NAME, create_user_details())
    assert usr.user_exists(usr.TEST_USER_NAME)
    # usr.delete_user(usr.TEST_USER_NAME)


def test_update_user_password():
    usr.update_user_password(usr.TEST_USER_NAME, NEW_TEST_PASSWORD)
    usr_dtls = usr.get_user_details(usr.TEST_USER_NAME)
    assert (usr_dtls[usr.PASSWORD] == NEW_TEST_PASSWORD)

def test_add_saved_recipe():
    usr.add_saved_recipe(usr.TEST_USER_NAME, TEST_RECIPE_ID)
    usr_dtls = usr.get_user_details(usr.TEST_USER_NAME)
    saved_recs = usr_dtls[usr.SAVED_RECIPES]
    print(f'{saved_recs=}')
    saved_rec_exists = False
    saved_recs_lst = saved_recs.split(';')
    for x in saved_recs_lst:
        if x == TEST_RECIPE_ID:
            saved_rec_exists = True
    assert (saved_rec_exists)


def test_remove_saved_recipe():
    usr.remove_saved_recipe(usr.TEST_USER_NAME, TEST_RECIPE_ID)
    usr_dtls = usr.get_user_details(usr.TEST_USER_NAME)
    saved_recs = usr_dtls[usr.SAVED_RECIPES]
    saved_rec_exists = False
    saved_recs_lst = saved_recs.split(';')
    for x in saved_recs_lst:
        if x == TEST_RECIPE_ID:
            saved_rec_exists = True
    assert (not saved_rec_exists)


def test_remove_all_saved_recipes():
    usr.remove_all_saved_recipes(usr.TEST_USER_NAME)
    usr_dtls = usr.get_user_details(usr.TEST_USER_NAME)
    saved_recs = usr_dtls[usr.SAVED_RECIPES]
    assert (saved_recs == '')


def test_delete_test_recipe():
    usr.delete_user(usr.TEST_USER_NAME)
    assert (not usr.user_exists(usr.TEST_USER_NAME))
