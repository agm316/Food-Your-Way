"""
This file will test our users db file users.py
"""
import os
import pytest
import db.users as usr

RUNNING_ON_CICD_SERVER = os.environ.get('CI', False)

TEST_DEL_NAME = 'User to be deleted'


def create_user_details():
    details = {}
    for field in usr.REQUIRED_FIELDS:
        details[field] = 2
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
    usr.delete_user(usr.TEST_USER_NAME)