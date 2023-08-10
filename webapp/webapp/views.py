from django.shortcuts import redirect
from django.shortcuts import render
import json
import logging
from email.message import EmailMessage
import base64
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from django.contrib.auth import authenticate, logout
from django.http import JsonResponse
from googleapiclient.errors import HttpError

from daemons.user_check_daemon import create_service
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
	"""Job submit checks if there are any pending or running jobs first for the user
	If yes, new job is updated with a status of “pending”
	If no, new job is updated with a status of “running”
"""
	data = json.loads(request.POST.dict()['obj'])
	conn = get_mongo()
	all_jobs = conn.AdNet.users.find_one({'id': request.user.email}, {'_id': 0, 'jobs': 1})['jobs']
	pending = False
	for job in all_jobs:
		if job['status'] == 'running' or job['status'] == 'pending':
			pending = True

	for job in all_jobs:
		if job['name'] == data['name']:
			job['status'] = 'running'
			if pending:
				job['status'] = 'pending'
	conn.AdNet.users.update_one({'id': request.user.email}, {"$set": {'jobs': all_jobs}})
	data['user_id'] = request.user.email
	url = 'http://138.49.185.228:5000/build'
	headers = {
		'Content-type': 'application/json',
		'Accept': 'application/json'
	}
	requests.post(url, json=data, headers=headers)
	return HttpResponse({'success': True})


def gmail_send_message(service, email, job_id):

	try:
		message = EmailMessage()
		message.set_content('Your results for job {} have been processed and are ready for viewing! Please sign in and check the results page to see how your neural network performed!'.format(job_id))
		message['To'] = email
		message['From'] = 'information@adnet.app'
		message['Subject'] = 'Results Ready for Viewing!'

		# encoded message
		encoded_message = base64.urlsafe_b64encode(message.as_bytes()) \
			.decode()

		create_message = {
			'raw': encoded_message
		}
		# pylint: disable=E1101
		send_message = (service.users().messages().send
						(userId="me", body=create_message).execute())
	except HttpError as error:
		send_message = None
	return send_message

@csrf_exempt
def process_results(request):
	"""
	Returned results are put into a results collection with the user email and job name (this combination will result in a unique search result
	Update job status as completed
	Check if there are any pending jobs for the user
	If yes, first pending job is sent via submit_job call
	If no, do nothing
	Send email
	"""
	os.chdir('/home/ubuntu/adnet/webapp/daemons/')
	data = json.loads(request.body)
	conn = get_mongo()
	# Returned results are put into a results collection with the user email and job name (this combination will result in a unique search result
	conn.AdNet.Results.insert_one({'job_id': data['job_id'], 'email': data['email'], 'results': data['results']})
	all_jobs = conn.AdNet.users.find_one({'id': request.user.email}, {'_id': 0, 'jobs': 1})['jobs']
	next_job = None
	for job in all_jobs:
		if job['name'] == data['name']:
			job['status'] = 'completed'
		if job['name'] != data['name'] and job['status'] == 'pending' and not next_job:
			next_job = job
			job['status'] = 'running'
	conn.AdNet.users.update_one({'id': data['email']}, {"$set": {'jobs': all_jobs}})
	service = create_service()
	gmail_send_message(service, data['email'], data['job_id'])
	if next_job:
		new_data = next_job
		new_data['user_id'] = data['email']
		url = 'http://138.49.185.228:5000/build'
		headers = {
			'Content-type': 'application/json',
			'Accept': 'application/json'
		}
		requests.post(url, json=new_data, headers=headers)
	return HttpResponse({'success': True})
