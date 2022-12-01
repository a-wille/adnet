import json
from django.http import HttpResponse
from django.shortcuts import render
from webapp.view_helpers import get_mongo


def index(request):
	"""returns home page"""
	return render(request, 'index.html')

def get_all_snps(request):
	"Get all names of SNPS for search bar"
	data = []
	conn = get_mongo()
	docs = conn.AdNet.SNPs.find({})
	for doc in docs:
		del(doc['_id'])
		data.append(doc)
	return HttpResponse(json.dumps(data))


def get_snp_data(request):
	post = request.POST.dict()
	if post == {}:
		return HttpResponse(json.dumps({}))
	conn = get_mongo()
	doc = conn.AdNet.SNPs.find_one({'snp_name': post['name']})
	del doc['_id']
	return HttpResponse(json.dumps(doc))