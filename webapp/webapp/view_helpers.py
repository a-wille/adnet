from pymongo import MongoClient

def get_mongo(**kwargs):
    # allows an instance of a mongo connection to allow for inserts, edits, and
    # deletes into the mongo database

    global _mongo_conn
    user = 'user'
    # user= 'user'
    pw = 'securityismypassion'
    _mongo_conn = MongoClient("mongodb+srv://adnet.khzkajw.mongodb.net/AdNet", username=user, password=pw)
    # _mongo_conn = MongoClient(connect=False, username=user, password=pw, authSource='nonprofit')
    return _mongo_conn
    # global _mongo_conn
    # _mongo_conn = MongoClient("mongodb+srv://user:securityismypassion@adnet.khzkajw.mongodb.net/?retryWrites=true&w=majority")
    # return _mongo_conn
