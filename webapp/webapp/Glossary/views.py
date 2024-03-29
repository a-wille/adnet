import json
from django.http import HttpResponse
from django.shortcuts import render
from webapp.view_helpers import get_mongo


def index(request):
	"""returns home page"""
	return render(request, 'index.html', {'active_tab':1})

def glossary_page(request):
	return render(request, 'glossary_index.html')

def get_all_terms(request):
	"""returns a list of all currently occurring and future events to volunteers and donors"""
	conn = get_mongo()
	data = list(conn.AdNet.Glossary.find({}, {'_id': 0}))
	return HttpResponse(json.dumps(data))

def get_term_definition(request):
	post = request.POST.dict()
	if post == {}:
		return HttpResponse(json.dumps({}))
	conn = get_mongo()
	if conn.AdNet.Glossary.find_one({'name': post['name']}):
		doc =  conn.AdNet.Glossary.find_one({'name': post['name']})
		return HttpResponse(json.dumps({'term': post['name'], 'definition': doc['definition']}))

def get_ml_terms(request):
	conn = get_mongo()
	data = list(conn.AdNet.Glossary.find({'type': 'ml'}, {'_id': 0}))
	return HttpResponse(json.dumps(data))

def get_g_terms(request):
	conn = get_mongo()
	data = list(conn.AdNet.Glossary.find({'type': 'g'}, {'_id': 0}))
	return HttpResponse(json.dumps(data))
