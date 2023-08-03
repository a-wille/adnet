from django.shortcuts import redirect
from django.shortcuts import render
import json
from django.db import IntegrityError
from django.contrib.auth import authenticate, logout
from webapp.models import User
from django.contrib.auth import login as login_django
from webapp.view_helpers import get_mongo
from django.http import HttpResponse
from django.contrib.auth.models import Group
import os
import requests
os.environ['CUDA_VISIBLE_DEVICES'] = "0"

location_class = {
	'intergenic_variant': '2',
	'regulatory_region_variant': '1',
	'TF_binding_site_variant': '1',
	'downstream_variant': '9',
	'upstream_variant': '2',
	'intron_variant': '6',
	'non_coding_transcript_exon_variant': '10',
	'3_prime_UTR_variant': '8',
	'5_prime_UTR_variant': '3',
	'synonymous_variant': '4',
	'splice_donor_variant': '5',
	'splice_region_variant': '6',
	'missense_variant': '4',
	'inframe_insertion': '4',
	'stop_gained': '4'
}
risk_level = {
	'HIGH': 4,
	'MODERATE': 3,
	'LOW': 2,
	'MODIFIER': 1
}

def index(request):
	# returns index page
	return render(request, 'index.html', {'active_tab': 0})

def glossary(request):
	return render(request, 'glossary_index.html')

def gene_search(request):
	return render(request, 'gene_search_index.html')

def snp_search(request):
	return render(request, 'snp_search_index.html')

def login(request):
	#returns html content for a window that you can log in with
	return render(request, 'login.html')

def home(request):
	#returns home tab
	return render(request, 'home.html')

def account_view(request):
	#returns html content for a window that you can make an account from
	return render(request, 'account_creation.html')

def build(request):
	return render(request, 'build_page.html')

def run(request):
	return render(request, 'run_page.html')

def create_account(request):
	"""creates an account for a user"""
	conn = get_mongo()
	try:
		email = request.POST.get('email').endswith('.edu')
		if not email:
			return HttpResponse({'non-educational email'})
	except:
		pass
	doc = conn.AdNet.users.find_one({'id': request.POST.get('email')})
	try:
		user = User.objects.create(firstname=request.POST.get('first'),
							   		lastname=request.POST.get('last'),
							   		institution=request.POST.get('institution'),
							   		email=request.POST.get('email'),
							   		password=request.POST.get('pass'),
								   	username=request.POST.get('email'),
							   )
		user.set_password(user.password)
		user.save()
		base_group = Group.objects.get(name='BaseUser')
		base_group.user_set.add(user)
	except IntegrityError as e:
		user = User.objects.get(email=request.POST.get('email'))
		if user and not doc:
			user.delete()
			user = User.objects.create(firstname=request.POST.get('first'),
									   lastname=request.POST.get('last'),
									   institution=request.POST.get('institution'),
									   email=request.POST.get('email'),
									   password=request.POST.get('pass'),
									   username=request.POST.get('email'),
									   )
			user.set_password(user.password)
			user.save()
			base_group = Group.objects.get(name='BaseUser')
			base_group.user_set.add(user)
			doc = {'firstname': user.firstname, 'lastname': user.lastname, 'password': user.password, 'id': user.email,
				   'institution': user.institution, 'status': 'unverified', 'email_sent': False, 'jobs': [],
				   'configs': []}
			conn.AdNet.users.insert_one(doc)
			login_django(request, user)
			return HttpResponse({'success': True})
		else:
			return HttpResponse({'duplicate_email'})
	except Exception as e:
		return HttpResponse({'error'})

	doc = {'firstname': user.firstname, 'lastname': user.lastname, 'password': user.password, 'id': user.email, 'institution': user.institution, 'status': 'unverified', 'email_sent': False, 'jobs': [], 'configs': []}
	conn.AdNet.users.insert_one(doc)
	login_django(request, user)
	return HttpResponse({'success': True})


def check_login(request):
	"""check if a user is authenticated or not"""
	conn = get_mongo()
	email = request.POST.get('user')
	password = request.POST.get('pass')
	user = authenticate(username=email, password=password)

	if user and user.email == request.POST.get('user'):
		doc = conn.AdNet.users.find_one({'id': email})
		if doc['status'] == 'verified':
			research_group = Group.objects.get(name='ResearchUser')
			research_group.user_set.add(user)
		login_django(request, user)
		return HttpResponse({'success': True})
	elif user:
		logout(request)
	return HttpResponse({'error': False})

def my_logout(request):
	"""logs out a user"""
	logout(request)
	return HttpResponse({'success': True})

def check_admin(request):
	"""checks if a user has admin permissions"""
	if request.user.has_perm('can_admin'):
		return HttpResponse({'success': True})
	return HttpResponse({'success': False})

def submit_job(request):
	data = json.loads(request.POST.dict()['obj'])
	data['user_id'] = request.user.email
	url = "http://138.49.185.228:5000/build/"
	headers = {
		'Content-type': 'application/json',
		'Accept': 'application/json'
	}
	requests.post(url, json=data, headers=headers)

	return HttpResponse({'okay': 'hi'})
