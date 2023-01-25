import json
from django.http import HttpResponse
from django.shortcuts import render

from webapp.GeneSearch.views import format_list
from webapp.view_helpers import get_mongo
from webapp.view_helpers import remove_substring_from_string


def index(request):
	"""returns home page"""
	return render(request, 'index.html')

def get_all_snps(request):
	"Get all names of SNPS for search bar"
	conn = get_mongo()
	docs = conn.AdNet.SNPs.find({}, {'_id': 1, 'chr': 1, 'chr_pos': 1,
									 'functional_class': 1, 'is_intergenic': 1,								 'risk_level': 1, 'genes': 1})
	return HttpResponse(json.dumps(list(docs)))

def get_all_names(request):
	"Get all names of SNPS for search bar"
	data = []
	conn = get_mongo()
	docs = conn.AdNet.SNPs.find({})
	for doc in docs:
		data.append({'snp': doc['snp_name']})
	return HttpResponse(json.dumps(data))

def get_snp_details(request):
	snp_id = remove_substring_from_string(request.path, '/SNPSearch/get_details/')
	return render(request, 'snp_information.html', {'content': snp_id})


def get_snp_data(request):
	snp_id = remove_substring_from_string(request.path, '/SNPSearch/GetSNPInfo/')
	conn = get_mongo()
	doc = conn.AdNet.SNPs.find_one({'snp_name': snp_id})
	doc['values'] = format_list(doc, 'values')
	doc['genes'] = format_list(doc, 'genes')
	del doc['_id']
	return HttpResponse(json.dumps(doc))