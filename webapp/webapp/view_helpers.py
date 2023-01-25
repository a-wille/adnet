from pymongo import MongoClient

def get_mongo(**kwargs):
    # allows an instance of a mongo connection to allow for inserts, edits, and
    # deletes into the mongo database

    global _mongo_conn
    user = 'user'
    pw = 'securityismypassion'
    _mongo_conn = MongoClient("mongodb+srv://adnet.khzkajw.mongodb.net/AdNet", username=user, password=pw)
    # _mongo_conn = MongoClient(connect=False, username=user, password=pw, authSource='nonprofit')
    return _mongo_conn
    # global _mongo_conn
    # _mongo_conn = MongoClient("mongodb+srv://user:securityismypassion@adnet.khzkajw.mongodb.net/?retryWrites=true&w=majority")
    # return _mongo_conn

def remove_substring_from_string(s, substr):
	"""helper function for parsing url for a particular string"""
	i = 0
	while i < len(s) - len(substr) + 1:
		if s[i:i + len(substr)] == substr:
			break
		i += 1
	else:
		return s
	return s[:i] + s[i + len(substr):]