

from pymongo import MongoClient

def get_mongo(**kwargs):
	#allows an instance of a mongo connection to allow for inserts, edits, and
	# deletes into the mongo database
	global _mongo_conn
	user='user'
	pw='securityismypassion'
	_mongo_conn = MongoClient("mongodb+srv://{}:{}@adnet.khzkajw.mongodb.net/?retryWrites=true&w=majority".format(user, pw))
	return _mongo_conn