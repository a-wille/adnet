import datetime
import pytz
from webapp.view_helpers import get_mongo
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
import json


def cancel(request):
    """Cancels a volunteer shift for a particular event"""
    conn = get_mongo()
    doc = conn.nonprofit.events.find_one({'id': int(request.POST.get('id'))})
    new_volunteers = doc['volunteers'].copy()
    new_volunteers.pop(new_volunteers.index(request.user.email))
    filter = {'id': int(request.POST.get('id'))}
    new_vals = {"$set": {'volunteers': new_volunteers}}
    conn.nonprofit.events.update_one(filter, new_vals)

    filter = {'id': request.user.email}
    events = conn.nonprofit.users.find_one({'id': request.user.email})['events'].copy()
    events.pop(int(events.index(int(request.POST.get('id')))))
    new_vals = {"$set": {'events': events}}
    conn.nonprofit.users.update_one(filter, new_vals)
    return HttpResponse({'success': 'true'})


def sign_up(request):
    """Signs user up for a volunteer shift for a particular event if possible"""
    conn = get_mongo()
    doc = conn.nonprofit.events.find_one({'id':int(request.POST.get('id'))})
    if len(doc['volunteers']) >= int(doc['volunteers_needed']):
        return HttpResponse(json.dumps({'success': 'false'}))

    #check that dates don't overlap
    events = conn.nonprofit.users.find_one({'id': request.user.email})['events'].copy()
    for e in events:
        d = conn.nonprofit.events.find_one({'id': int(e)})
        start1 = d['start']
        end1 = d['end']
        start2 = doc['start']
        end2 = doc['end']
        if start1 <= end2 and start2 <= end1:
            # if dates overlap, can't sign up for that new shift
            return HttpResponse(json.dumps({'success': 'false'}))

    # updating mongo records
    new_volunteers = doc['volunteers'].copy()
    new_volunteers.append(request.user.email)
    filter = {'id': int(request.POST.get('id'))}
    new_vals = { "$set": {'volunteers': new_volunteers}}
    conn.nonprofit.events.update_one(filter, new_vals)

    filter = {'id': request.user.email}
    events.append(int(request.POST.get('id')))
    new_vals = {"$set": {'events': events}}
    conn.nonprofit.users.update_one(filter, new_vals)
    return HttpResponse({'success': 'true'})


def get_active(request):
    """returns a list of all currently active users"""
    conn = get_mongo()
    data = []
    docs = conn.nonprofit.users.find({})
    for doc in docs:
        doc['admin'] = None
        if doc['id'] == 'admin@gmail.com':
            doc['admin'] = 'true'
        doc.pop('_id')
        doc.pop('password')
        data.append(doc)
    return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder))

def get_inactive(request):
    """returns a list of all currently inactive or deactivated users"""
    conn = get_mongo()
    data = []
    docs = conn.nonprofit.inactive_users.find({})
    for doc in docs:
        doc['admin'] = None
        if doc['id'] == 'admin@gmail.com':
            doc['admin'] = 'true'
        doc.pop('_id')
        data.append(doc)
    return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder))

def deactivate(request):
    """deactivate a user account"""
    conn = get_mongo()
    doc = conn.nonprofit.users.find_one({'id': request.POST['id']})
    now = datetime.datetime.now()
    if doc['user'] == request.user.username:
        return HttpResponse('nope')
    events = doc['events']

    # remove user from all events that they have signed up to volunteer for
    for event in events:
        doc = conn.nonprofit.events.find_one({'id': event})
        if doc and doc['start'] > now:
            original_volunteers = doc['volunteers']
            new_volunteers = original_volunteers.copy()
            new_volunteers.pop(new_volunteers.index(request.POST['id']))
            filter = {'id': event}
            new_vals = {'$set': {'volunteers': new_volunteers}}
            conn.nonprofit.events.update_one(filter, new_vals)

    # update mongo records
    doc = conn.nonprofit.users.find_one({'id': request.POST['id']})
    conn.nonprofit.inactive_users.insert(doc)
    conn.nonprofit.users.remove({'id': request.POST['id']})
    return HttpResponse('Good')

def activate(request):
    """activate a user account"""
    conn = get_mongo()
    doc = conn.nonprofit.inactive_users.find_one({'id': request.POST['id']})
    conn.nonprofit.users.insert(doc)
    conn.nonprofit.inactive_users.remove({'id': request.POST['id']})
    return HttpResponse('Good')


def get_volunteer_events(request):
    """get all events that a user is signed up to volunteer at"""
    data = []
    conn = get_mongo()
    email = request.user.email
    if email == '':
        email = 'admin@gmail.com'
    doc = conn.nonprofit.users.find_one({'id': email})
    dt = datetime.datetime.now(tz=pytz.timezone("US/Central"))
    event_list = []
    for e in doc['events']:
        event_list.append(e)
    for e in event_list:
        doc = conn.nonprofit.events.find_one({'id': e})
        doc.pop('_id')
        doc.pop('donations')
        doc['volunteers_needed'] = int(doc['volunteers_needed']) - len(doc['volunteers'])
        doc.pop('volunteers')
        doc['endnew'] = pytz.timezone("US/Central").localize(doc['end'])
        if doc['endnew'] > dt:
            data.append(doc)
    return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder))

def get_all_events(request):
    #kinda a lie, returns all events that the user isn't actively signed up for
    data = []
    conn = get_mongo()
    dt = datetime.datetime.now(tz=pytz.timezone("US/Central"))
    docs = conn.nonprofit.events.find({})
    for doc in docs:
        already_volunteering = 0
        for v in doc['volunteers']:
            if v == request.user.email:
                already_volunteering = 1
        if not already_volunteering:
            doc.pop('_id')
            doc.pop('donations')
            doc['volunteers_needed'] = int(doc['volunteers_needed']) - len(doc['volunteers'])
            doc.pop('volunteers')
            doc['endnew'] = pytz.timezone("US/Central").localize(doc['end'])
            if doc['endnew'] > dt and doc['volunteers_needed'] != 0:
                data.append(doc)
    return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder))