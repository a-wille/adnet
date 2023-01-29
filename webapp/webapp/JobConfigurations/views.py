import json
from django.http import HttpResponse
from django.shortcuts import render

from webapp.GeneSearch.views import format_list
from webapp.view_helpers import get_mongo
from webapp.view_helpers import remove_substring_from_string

def get_all_jobs(request):
    email = request.user.email
    conn = get_mongo()
    doc = conn.AdNet.users.find_one({'id': email})
    return HttpResponse(json.dumps(doc['jobs']))

def get_all_options(request):
    conn = get_mongo()
    gene_docs = list(conn.AdNet.Genes.find({}, {'_id': 1}))
    snp_docs = list(conn.AdNet.SNPs.find({}, {'_id': 1}))
    return HttpResponse(json.dumps(gene_docs+snp_docs))


def create(request):
    info = request.GET.dict()
    conn = get_mongo()
    user_doc = conn.AdNet.users.find_one({'id': request.user.email})
    new_config = {'name': info['name'], 'one': info['one'], 'two': info['two'],
                  'three': info['three'], 'four': info['four'], 'five': info['five'], 'ml_configs': [], 'status': 'draft'}
    new_jobs = user_doc['jobs'] + [(new_config)]
    conn.AdNet.users.update_one({'id': request.user.email}, {"$set": {'jobs': new_jobs}})
    return HttpResponse({'success': True})

def edit(request):
    info = request.GET.dict()
    conn = get_mongo()
    user_doc = conn.AdNet.users.find_one({'id': request.user.email})
    new_config = {'name': info['name'], 'one': info['one'], 'two': info['two'],
                  'three': info['three'], 'four': info['four'], 'five': info['five'], 'ml_configs': [],
                  'status': info['status']}
    updated_jobs = []
    for job in user_doc['jobs']:
        if job['name'] != info['og_id']:
            updated_jobs.append(job)
    updated_jobs.append(new_config)
    conn.AdNet.users.update_one({'id': request.user.email}, {"$set": {'jobs': updated_jobs}})
    return HttpResponse({'success': True})

def delete(request):
    info = request.GET.dict()
    conn = get_mongo()
    user_doc = conn.AdNet.users.find_one({'id': request.user.email})
    updated_jobs = []
    for job in user_doc['jobs']:
        if job['name'] != info['name']:
            updated_jobs.append(job)
    conn.AdNet.users.update_one({'id': request.user.email}, {"$set": {'jobs': updated_jobs}})
    return HttpResponse({'success': True})