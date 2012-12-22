import pymongo

def get_connection(database):
    return pymongo.MongoClient()[database]
