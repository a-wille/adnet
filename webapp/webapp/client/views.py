import datetime
from django.shortcuts import render
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate, logout
from webapp.models import User
from django.contrib.auth import login as login_django
from webapp.extra.view_helper import get_mongo
import pytz
from django.http import HttpResponse


def index(request):
	# returns index page
	return render(request, 'index.html')

def events(request):
	# returns events page
	return render(request, 'events.html')

def donate(request):
	#returns donate page
	return render(request, 'donate.html')

def volunteer(request):
	#returns volunteer page
	return render(request, 'volunteer.html')

def all_events(request):
	#returns all events page for admin
	return render(request, 'all_events.html')

def all_volunteers(request):
	#returns all users page for admin
	return render(request, 'all_users.html')

def login(request):
	#returns html content for a window that you can log in with
	return render(request, 'login.html')

def home(request):
	#returns home tab
	return render(request, 'home.html')

def account_view(request):
	#returns html content for a window that you can make an account from
	return render(request, 'account_creation.html')

def user_manual(request):
	#returns user manual page
	return render(request, 'user_manual.html')

def donation_unrestricted(request):
	#returns html content for a window that you use to make an unrestricted donation
	return render(request, 'unrestricted_donation.html')


def remove_substring_from_string(s, substr):
	"""helper function for parsing url for a particular string"""
	i = 0
	while i < len(s) - len(substr) + 1:
		if s[i:i + len(substr)] == substr:
			break
		i += 1
	else:
		return s
	return s[:i] + s[i + len(substr):]

def donation_restricted(request):
	#returns html content for a window that you can make a restricted donation from
	event_id = int(remove_substring_from_string(request.path, '/client/donate_restricted/'))
	return render(request, 'restricted_donation.html', context={'event_id': event_id})


def user_summary(request):
	"""returns a user summary report for the admin to view"""
	user_id = str(remove_substring_from_string(request.path, '/client/user_summary/'))
	conn = get_mongo()
	now = datetime.datetime.now()
	doc = conn.nonprofit.users.find_one({'id': user_id})
	if not doc:
		doc = conn.nonprofit.inactive_users.find_one({'id': user_id})
	my_context = {}
	my_context['user_id'] = user_id
	my_context['name'] = doc['user']
	hours = 0
	past_events = "";
	#get all events that a user has volunteered for in the past and calculates total volunteer hours
	if doc['volunteer']:
		for event in doc['events']:
			edoc = conn.nonprofit.events.find_one({'id': event})
			if edoc and edoc['start'] > now:
				diff = edoc['end'] - edoc['start']
				diff_in_hours = diff.total_seconds() / 3600
				hours += diff_in_hours
				past_events += "{}\n{}\nId: {}\n\n".format(edoc['name'],
														   edoc['start'].strftime("%Y-%m-%d %H:%M %p"),
														   edoc['id'])
	my_context['volunteer_hours'] = hours

	#get all donations that a user has made and calculate total donations made
	donations = 0
	past_donations = ""
	if doc['donor']:
		ddocs = conn.nonprofit.donations.find({'user': user_id})
		for do in ddocs:
			donations += int(do['amount'])
			event_name = "None"
			if do['type'] == 'restricted':
				event = conn.nonprofit.events.find_one({'id': do['event_id']})
				if event:
					event_name = event_name['name']
			past_donations += "{}\nAmount: ${}\nType of Donation: {}\nEvent Name (if applicable): {}\n\n".format(
													   do['date'].strftime("%Y-%m-%d %H:%M"),
													   do['amount'],
													   do['type'], event_name)
	my_context['donations'] = donations
	# set context variables to load in which permissions a user has to display in the report
	permissions = ""
	if doc['volunteer']:
		permissions += "Volunteer, "
		my_context['volunteer'] = True
	if doc['donor']:
		permissions += "Donor, "
		my_context['donor'] = True
	if doc['user'] == "admin":
		permissions += "Admin, "
	my_context['permissions'] = permissions[:-2]
	my_context['past_donations'] = past_donations
	my_context['past_events'] = past_events
	return render(request, 'report.html', context=my_context)


def make_restricted_donation(request):
	"""function for a user to make a restricted donation to an event"""
	conn = get_mongo()
	greatest_id = 0
	all = conn.nonprofit.donations.find({})
	for a in all:
		if a['donation_id'] > greatest_id:
			greatest_id = a['donation_id']
	post = request.POST.dict()
	doc = {'donation_id': greatest_id +1, 'date': datetime.datetime.now(tz=pytz.timezone('US/Central')), 'user': request.user.email, 'amount': post['currency'], 'type': 'restricted', 'event_id': post['id']}
	conn.nonprofit.donations.insert(doc)
	return HttpResponse({'success': 'true'})

def make_unrestricted_donation(request):
	"""function for a user to make an unrestricted donation"""
	conn = get_mongo()
	greatest_id = 0
	all = conn.nonprofit.donations.find({})
	for a in all:
		if a['donation_id'] > greatest_id:
			greatest_id = a['donation_id']
	post = request.POST.dict()
	doc = {'donation_id': greatest_id +1, 'date': datetime.datetime.now(tz=pytz.timezone('US/Central')), 'user': request.user.email, 'amount': post['currency'], 'type': 'unrestricted', 'event_id': -1}
	conn.nonprofit.donations.insert(doc)
	return HttpResponse({'success': 'true'})

def create_account(request):
	"""creates an account for a user"""
	user = User.objects.create(username=request.POST.get('user'),
							   email=request.POST.get('email'),
							   password=request.POST.get('pass'),
							   )
	user.is_active = True
	user.set_password(user.password)
	user.save()
	conn = get_mongo()
	doc = {'user': user.username, 'password': user.password, 'id': user.email, 'events': [], 'donations': [], 'volunteer': request.POST.get('volunteer'), 'donor': request.POST.get('donor')}
	conn.nonprofit.users.insert(doc)
	if request.POST.get('donor') == 'true':
		donor_group = Group.objects.get(name='donor')
		donor_group.user_set.add(user)

	if request.POST.get('volunteer') == 'true':
		v_group = Group.objects.get(name='volunteer')
		v_group.user_set.add(user)

	user = authenticate(username=request.POST.get('user'), password=request.POST.get('pass'))

	if user:
		login_django(request, user)
		return HttpResponse({'success': True})


def check_login(request):
	"""check if a user is authenticated or not"""
	username = request.POST.get('user')
	password = request.POST.get('pass')
	user = authenticate(username=username, password=password)

	if user:
		login_django(request, user)
		return HttpResponse({'success': True})
	return HttpResponse({'success': False})

def my_logout(request):
	"""logs out a user"""
	logout(request)
	return HttpResponse({'success': True})

def check_admin(request):
	"""checks if a user has admin permissions"""
	if request.user.has_perm('can_admin'):
		return HttpResponse({'success': True})
	return HttpResponse({'success': False})