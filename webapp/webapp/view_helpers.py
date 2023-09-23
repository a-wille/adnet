from pymongo import MongoClient
from webapp.settings import MONGO_USER, MONGO_PASS

def get_mongo(**kwargs):
    # allows an instance of a mongo connection to allow for inserts, edits, and
    # deletes into the mongo database
    global _mongo_conn

    _mongo_conn = MongoClient("mongodb+srv://adnet.khzkajw.mongodb.net/AdNet", username=MONGO_USER, password=MONGO_PASS)
    return _mongo_conn


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