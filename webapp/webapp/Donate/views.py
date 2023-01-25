import datetime
import json
import pytz
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from webapp.view_helpers import get_mongo


def get_all_events(request):
	"""returns all currently occurring or future events to Donate tab"""
	data = []
	conn = get_mongo()
	docs = conn.webapp.events.find({})
	dt = datetime.datetime.now(tz=pytz.timezone("US/Central"))
	for doc in docs:
		doc.pop('_id')
		doc.pop('volunteers')
		doc.pop('donations')
		doc.pop('volunteers_needed')
		doc.pop('description')
		doc['endnew'] = pytz.timezone("US/Central").localize(doc['end'])
		if doc['endnew'] > dt:
			data.append(doc)
	return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder))


def get_my_donations(request):
	"""returns a list of all donations a donor has made to the donate page"""
	conn = get_mongo()
	data = []
	docs = conn.nonprofit.donations.find({'user': request.user.email})
	for doc in docs:
		if doc['event_id'] != -1:
			e = conn.nonprofit.events.find_one({'id': int(doc['event_id'])})
			doc['event_id'] = e['name']
		else:
			doc['event_id'] = "N/A"
		doc.pop('_id')
		doc.pop('user')
		doc.pop('donation_id')
		doc['dark'] = pytz.timezone("UTC").localize(doc['date']).astimezone(pytz.timezone("US/Central")).strftime("%m/%d/%y")
		doc['darktime'] = pytz.timezone("UTC").localize(doc['date']).astimezone(pytz.timezone("US/Central")).strftime("%H:%M")
		doc.pop('date')
		data.append(doc)
	return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder))