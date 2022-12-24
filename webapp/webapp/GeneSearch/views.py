import json
from django.http import HttpResponse
from django.shortcuts import render

from webapp.client.views import remove_substring_from_string
from webapp.view_helpers import get_mongo


def index(request):
	"""returns home page"""
	return render(request, 'index.html')

def get_all_genes(request):
	"Get all names of SNPS for search bar"
	data = []
	conn = get_mongo()
	docs = conn.AdNet.Genes.find({})
	for doc in docs[0:10]:
		del(doc['_id'])
		data.append(doc)
	return HttpResponse(json.dumps(data))

def get_all_names(request):
	"Get all names of SNPS for search bar"
	data = []
	conn = get_mongo()
	docs = conn.AdNet.Genes.find({})
	for doc in docs:
		data.append({'gene': doc['name']})
	return HttpResponse(json.dumps(data))


def get_gene_data(request):
	post = request.POST.dict()
	if post == {}:
		return HttpResponse(json.dumps({}))
	conn = get_mongo()
	doc = conn.AdNet.Genes.find_one({'snp_name': post['name']})
	del doc['_id']
	return HttpResponse(json.dumps(doc))

def get_gene_info(request):
	gene_id = remove_substring_from_string(request.path, '/GeneSearch/GetGeneInfo/')
	conn = get_mongo()
	doc = conn.AdNet.Genes.find_one({'name': gene_id})
	del(doc['_id'])
	validated_data = {}
	for feature in doc.keys():
		if doc[feature] != None and doc[feature] != [] and doc[feature] != {}:
			validated_data[feature] = doc[feature]
	if 'expression' in validated_data.keys():
		validated_data['expression'] = format_expression(validated_data)
	if 'rna_sequences' in validated_data.keys():
		validated_data['rna_sequences'] = format_sequences(validated_data)
	validated_data['mod'] = format_snps(validated_data, 'mod')
	validated_data['nonmod'] = format_snps(validated_data, 'nonmod')
	return HttpResponse(json.dumps(validated_data))

def format_snps(data, arg):
	new_snps = []
	k = 'non_modifying'
	if arg == 'mod':
		k = 'modifying'
	for l in data['snp_list'][k]:
		new_snps.append({'text': l})
	return new_snps

def format_expression(data):
	new_expression = []
	for item in data['expression'].keys():
		new_expression.append({'value': float(data['expression'][item]),
							   'tissue': item})
	return new_expression

def format_sequences(data):
	sequences = []
	for item in data['rna_sequences']:
		sequences.append({'text': 'Transcript {}'.format(item['transcript']), 'items': [{'text': item['seq'] + '\t'}]})
	return sequences