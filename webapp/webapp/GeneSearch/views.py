import json
from django.http import HttpResponse
from django.shortcuts import render

from webapp.client.views import remove_substring_from_string
from webapp.view_helpers import get_mongo


def index(request):
	"""returns home page"""
	return render(request, 'index.html')

def get_all_genes(request):
	conn = get_mongo()
	docs = conn.AdNet.Genes.find({}, {'name': 1, 'chromosome': 1, 'type': 1, 'range': 1,
									  'description': 1, 'mod_len': 1, 'nm_len': 1})
	return HttpResponse(json.dumps(list(docs)))


def get_all_names(request):
	conn = get_mongo()
	docs = conn.AdNet.Genes.find({}, {'name': 1})
	return HttpResponse(json.dumps(list(docs)))


def get_gene_data(request):
	post = request.POST.dict()
	if post == {}:
		return HttpResponse(json.dumps({}))
	conn = get_mongo()
	doc = conn.AdNet.Genes.find_one({'snp_name': post['name']})
	return HttpResponse(json.dumps(doc))

def get_gene_info(request):
	gene_id = remove_substring_from_string(request.path, '/GeneSearch/GetGeneInfo/')
	conn = get_mongo()
	doc = conn.AdNet.Genes.find_one({'name': gene_id})
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
	validated_data['locations'] = format_list(validated_data, 'locations')
	validated_data['cofactors'] = format_list(validated_data, 'cofactors')
	validated_data['catalytic_activity'] = format_list(validated_data, 'catalytic_activity')
	for item in validated_data['snp_effects']:
		f = item['affected_features']
		item['affected_features'] = '{} ({}-{})'.format(f['type'], f['location']['start']['value'],
															  f['location']['end']['value'])
		if f['description'] != '':
			item['affected_features'] += ', ' + f['description']
	return HttpResponse(json.dumps(validated_data))


def format_list(data, arg):

	convert_str = ''
	if arg in data.keys():
		data[arg] = sorted(set(data[arg]), key=len)
		data[arg].reverse()
		i = 0
		for item in data[arg]:
			if item not in convert_str:
				if i != 0:
					convert_str += ', {}'.format(item)
				else:
					convert_str += item
					i = 1
	else:
		convert_str = 'Unknown'
	return convert_str


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