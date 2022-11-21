"""
This file will test if we are getting the recipes from the database.
"""
import pymongo as pm
import pytest
import db_connect as dbc

TEST_DB = dbc.GAME_DB
TEST_COLLECT = 'test_collect'
# can be used for field and value:
TEST_NAME = 'test'