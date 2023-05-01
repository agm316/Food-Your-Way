import os

import pymongo as pm

import pytest

import db.db_connect as dbc

RUNNING_ON_CICD_SERVER = os.environ.get('CI', False)

TEST_DB = dbc.RECIPE_DB
TEST_COLLECT = 'test_collect'
# can be used for field and value:
TEST_NAME = 'test'
TEST_KEY = 'recipe_name'
TEST_KEY_NAME = 'TESTTESTTESTTESTTEST'
NEW_TEST_KEY_NAME = 'NEWTESTTESTTESTTEST'
TEST_RECORD = {TEST_KEY: TEST_KEY_NAME}
NEW_TEST_RECORD = {TEST_KEY: NEW_TEST_KEY_NAME}

@pytest.fixture(scope='function')
def temp_rec():
    dbc.connect_db()
    dbc.client[TEST_DB][TEST_COLLECT].insert_one({TEST_NAME: TEST_NAME})
    # yield to our test function
    yield
    dbc.client[TEST_DB][TEST_COLLECT].delete_one({TEST_NAME: TEST_NAME})


def test_fetch_one(temp_rec):
    ret = dbc.fetch_one(TEST_COLLECT, {TEST_NAME: TEST_NAME})
    assert ret is not None


def test_fetch_one_not_there(temp_rec):
    ret = dbc.fetch_one(TEST_COLLECT, {TEST_NAME: 'not a field value in db!'})
    assert ret is None


def test_fetch_all():
    ret = dbc.fetch_all(TEST_COLLECT, TEST_DB)
    assert (isinstance(ret, list))


def test_fetch_all_filter():
    ret = dbc.fetch_all_filter(TEST_COLLECT, {}, TEST_DB)
    assert (isinstance(ret, list))


def test_fetch_all_as_dict():
    ret = dbc.fetch_all_as_dict(TEST_KEY, TEST_COLLECT, TEST_DB)
    assert (isinstance(ret, dict))


def test_insert_one():
    if (dbc.fetch_one(TEST_COLLECT, TEST_RECORD, TEST_DB) is not None):
        dbc.del_one(TEST_COLLECT, TEST_RECORD, TEST_DB)
    if (dbc.fetch_one(TEST_COLLECT, TEST_RECORD, TEST_DB) is not None):
        print('test_db_connect.py:    test_insert_one: Error Deleting')
        assert False
    else:
        ret = dbc.insert_one(TEST_COLLECT, TEST_RECORD, TEST_DB)
        assert (dbc.fetch_one(TEST_COLLECT, TEST_RECORD, TEST_DB) is not None)


def test_update_one():
    newvals = {"$set": NEW_TEST_RECORD}
    ret = dbc.update_one(TEST_COLLECT, TEST_RECORD, newvals, TEST_DB)
    assert (dbc.fetch_one(TEST_COLLECT, NEW_TEST_RECORD, TEST_DB) is not None)
        
def test_delete_one():
    ret = dbc.del_one(TEST_COLLECT, NEW_TEST_RECORD, TEST_DB)
    assert ((dbc.fetch_one(TEST_COLLECT, NEW_TEST_RECORD, TEST_DB)) is None)
