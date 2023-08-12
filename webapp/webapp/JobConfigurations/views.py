import json
from django.http import HttpResponse
from django.shortcuts import render

from webapp.view_helpers import get_mongo, remove_substring_from_string


def get_all_jobs(request):
    email = request.user.email
    conn = get_mongo()
    doc = conn.AdNet.users.find_one({'id': email})
    return HttpResponse(json.dumps(doc['jobs']))

def get_ml_configurations(request):
    job_id = remove_substring_from_string(request.path, 'JobConfigurations/GetMLConfigurations/')[1:-1]
    return render(request, 'ml_configurations.html', {'content': job_id})

def get_completed_jobs(request):
    conn = get_mongo()
    email = request.user.email
    doc = conn.AdNet.users.find_one({'id': email})
    jobs = doc['jobs']
    completed_jobs = []
    for job in jobs:
        if job['status'] == 'completed':
            completed_jobs.append(job)
    return HttpResponse(json.dumps(completed_jobs))

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

def check_if_possible(job, item):
    keys = ['one', 'two', 'three', 'four', 'five']
    full = True
    possible = True
    for k in keys:
        if job[k] == '':
            full = False
        if job[k] == item:
            possible = False
    if possible and not full:
        return True
    return False

def get_add_jobs(request):
    d = request.GET.dict()
    email = request.user.email
    conn = get_mongo()
    doc = conn.AdNet.users.find_one({'id': email})
    jobs = doc['jobs']
    edited_jobs = []
    for job in jobs:
        del job['ml_configs']
        del job['status']
        job['_id'] = job['name']
        del job['name']
        possible = check_if_possible(job, d['item'])
        if possible:
            edited_jobs.append(job)
    return HttpResponse(json.dumps(edited_jobs))

def get_ml_for_job(request):
    job_id = remove_substring_from_string(request.path, '/JobConfigurations/GetMLForJob/')
    user = request.user.email
    conn = get_mongo()
    jobs = conn.AdNet.users.find_one({'id': user})['jobs']
    ml_configs = None
    for job in jobs:
        if job['name'] == job_id:
            if job['ml_configs'] == []:
                # prepopulate with default values
                job['ml_configs'] = {
                    'layers': [{'number': 1, 'size': 64, 'activation': 'relu'},
                               {'number': 2, 'size': 64, 'activation': 'relu'}],
                    'final_activation': 'sigmoid',
                    'optimizer': 'adam',
                    'loss': 'binary_crossentropy',
                    'epochs': 10,
                    'batch_size': 32
                }
                conn.AdNet.users.update_one({'id': request.user.email}, {"$set": {'jobs': jobs}})
            ml_configs = job['ml_configs']

    return HttpResponse(json.dumps(ml_configs))

def set_ml_configs(request):
    data = json.loads(request.body)
    conn = get_mongo()
    jobs = conn.AdNet.users.find_one({'id': request.user.email})['jobs']

    for job in jobs:
        if job['name'] == data['job_id']:
            job['ml_configs'] = data['ml_configs']
    conn.AdNet.users.update_one({'id': request.user.email}, {"$set": {'jobs': jobs}})

    return HttpResponse({})

def add_item(request):
    keys = ['one', 'two', 'three', 'four', 'five']
    info = request.POST.dict()
    email = request.user.email
    conn = get_mongo()
    jobs = conn.AdNet.users.find_one({'id': email})['jobs']
    entered = False
    for job in jobs:
        if job['name'] == info['name']:
            for k in keys:
                if job[k] == '' and not entered:
                    job[k] = info['item']
                    entered = True
    if entered == False:
        return HttpResponse({'error'})
    conn.AdNet.users.update_one({'id': request.user.email}, {"$set": {'jobs': jobs}})
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