import os
import pymongo as pm
import certifi


LOCAL = "0"
CLOUD = "1"

# Run "docker-compose up -d" to start the docker container
# Run "docker-compose down" to stop the docker container
# Open Mongo Compass and connect to the database using Username/Password
# authentication method under Advanced Connection Options
RECIPE_DB = 'api_dev_db'

client = None


def connect_db():
    """
    This provides a uniform way to connect to the DB across all uses.
    Returns a mongo client object... maybe we shouldn't?
    Also set global client variable.
    We should probably either return a client OR set a
    client global.
    """
    global client
    if client is None:  # not connected yet!
        print("Setting client because it is None.")
        if os.environ.get("CLOUD_MONGO", LOCAL) == CLOUD:
            password = os.environ.get("MONGO_CLOUD_PSWRD")
            user = os.environ.get("MONGO_CLOUD_USER")
            if not password:
                raise ValueError('Cloud Password Not Set in Env Varia'
                                 + 'bles. Please Set and Try Again.')
            print("Connecting to Mongo in the CLOUD.")
            client = pm.MongoClient(f'mongodb+srv://{user}:{password}'
                                    + '@cluster0.catgdge.mongodb.net/'
                                    + '?retryWrites=true&w=majority',
                                    tlsCAFile=certifi.where())
        else:
            print("Connecting to Mongo Locally.")
            local_user = os.environ.get("MONGO_USER")
            local_passwrd = os.environ.get("MONGO_PASSWORD")
            client = pm.MongoClient(f'mongodb://{local_user}:'
                                    + f'{local_passwrd}@'
                                    + '127.0.0.1:27017')


def insert_one(collection, doc, db=RECIPE_DB):
    """
    Insert a single doc into collection.
    """
    print(f'{db=}')
    client[db][collection].insert_one(doc)


def fetch_one(collection, filt, db=RECIPE_DB):
    """
    Find with a filter and return on the first doc found.
    """
    for doc in client[db][collection].find(filt):
        return doc


def del_one(collection, filt, db=RECIPE_DB):
    """
    Find with a filter and return on the first doc found.
    """
    client[db][collection].delete_one(filt)


def fetch_all(collection, db=RECIPE_DB):
    ret = []
    for doc in client[db][collection].find():
        ret.append(doc)
    return ret


def fetch_all_as_dict(key, collection, db=RECIPE_DB):
    ret = {}
    for doc in client[db][collection].find():
        del doc['_id']
        ret[doc[key]] = doc
    return ret
