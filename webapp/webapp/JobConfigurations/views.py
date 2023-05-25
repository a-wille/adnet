import json
from django.http import HttpResponse
from webapp.view_helpers import get_mongo

def get_all_jobs(request):
    email = request.user.email
    conn = get_mongo()
    doc = conn.AdNet.users.find_one({'id': email})
    return HttpResponse(json.dumps(doc['jobs']))


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