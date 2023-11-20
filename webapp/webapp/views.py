import base64
import json
import os
from email.message import EmailMessage

from django.contrib.auth import login as login_django
import requests
from django.contrib.auth import authenticate, logout
from django.contrib.auth.models import Group
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from googleapiclient.errors import HttpError
from password_generator import PasswordGenerator

from daemons.user_check_daemon import create_service, check_user_accounts
from webapp.models import User
from webapp.settings import BUILD_URL
from webapp.view_helpers import get_mongo, remove_substring_from_string

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
    # returns html content for a window that you can log in with
    return render(request, 'login.html')


def home(request):
    # returns home tab
    return render(request, 'home.html')


def accounts_view(request):
    return render(request, 'accounts_view.html')


def account_view(request):
    # returns html content for a window that you can make an account from
    return render(request, 'account_creation.html')


def get_change_pass_window(request):
    username = remove_substring_from_string(request.path, '/change_pass_window/')
    print(username)
    return render(request, 'change_password.html', {'username': username})


def build(request):
    return render(request, 'jobs_page.html')


def run(request):
    return render(request, 'results_tab.html')


def create_account(request):
    """creates an account for a user"""
    conn = get_mongo()
    password = PasswordGenerator().generate()
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
                                   username=request.POST.get('email'),
                                   password=password,
                                   )
        user.set_password(password)
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
                                       username=request.POST.get('email'),
                                       password=password,
                                       )
            user.set_password(password)
            user.save()
            base_group = Group.objects.get(name='BaseUser')
            base_group.user_set.add(user)
            doc = {'firstname': user.firstname, 'lastname': user.lastname, 'id': user.email,
                   'institution': user.institution, 'status': 'first_time', 'email_sent': False, 'jobs': [],
                   'configs': []}
            conn.AdNet.users.insert_one(doc)
            service = create_service()
            gmail_verify(service, user.email, password)
            return HttpResponse({'success': True})
        else:
            return HttpResponse({'duplicate_email'})

    except Exception as e:
        return HttpResponse({'error'})

    doc = {'firstname': user.firstname, 'lastname': user.lastname, 'password': password, 'id': user.email,
           'institution': user.institution, 'status': 'first_time', 'email_sent': False, 'jobs': [], 'configs': []}
    conn.AdNet.users.insert_one(doc)
    service = create_service()
    gmail_verify(service, user.email, password)
    return HttpResponse({'success': True})

def get_unverified_users(request):
    conn = get_mongo()
    users = list(conn.AdNet.users.find({'status': 'unverified'}, {'_id': 0}))
    return HttpResponse(json.dumps(users))

def delete_user(request):
    data = request.POST.dict()
    conn = get_mongo()
    conn.AdNet.users.delete_one({'id': data['username']})
    user = User.objects.get(email=request.POST.get('email'))
    if user:
        user.delete()
    return HttpResponse({'success': True})

def approve_user(request):
    data = request.POST.dict()
    conn = get_mongo()
    conn.AdNet.users.update_one({'id': data['username']}, {"$set": {'status': 'verified'}})
    service = create_service()
    check_user_accounts(service)
    return HttpResponse({'success': True})


def check_login(request):
    """check if a user is authenticated or not"""
    conn = get_mongo()
    email = request.POST.get('user')
    password = request.POST.get('pass')
    user = authenticate(username=email, password=password)

    if user and user.email == request.POST.get('user'):
        doc = conn.AdNet.users.find_one({'id': email})
        login_django(request, user)
        if doc['status'] == 'verified':
            research_group = Group.objects.get(name='ResearchUser')
            research_group.user_set.add(user)
        if doc['status'] == 'first_time':
            base_group = Group.objects.get(name='BaseUser')
            base_group.user_set.add(user)
            login(request)
            return HttpResponse(json.dumps({'status': 'first_time', 'username': email}))
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
    pending_count = 1
    for job in all_jobs:
        if job['status'] == 'running' or 'pending' in job['status']:
            pending = True
            if 'pending' in job['status']:
                pending_count += 1
    for job in all_jobs:
        if job['name'] == data['name']:
            job['status'] = 'running'
            if pending:
                job['status'] = 'pending ({})'.format(pending_count)
    data['user_id'] = request.user.email
    url = BUILD_URL
    headers = {
        'Content-type': 'application/json',
        'Accept': 'application/json'
    }
    if not pending:
        requests.post(url, json=data, headers=headers)
    conn.AdNet.users.update_one({'id': request.user.email}, {"$set": {'jobs': all_jobs}})
    return HttpResponse({'success': True})


def gmail_send_message(service, email, job_id):
    try:
        message = EmailMessage()
        message.set_content(
            'Your results for job {} have been processed and are ready for viewing! Please sign in and check the results page to see how your neural network performed!'.format(
                job_id))
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

def gmail_send_error_message(service, email, job_id):
    try:
        message = EmailMessage()
        message.set_content(
            'Your job with ID {} has encountered an error and '
            'did your model was not successfully generated. An administrator has been contacted '
            'for further support, and your job has been reverted back to \'draft\' status. '
            ' Please wait for further details from an administrator regarding your error before '
            'resubmitting your job. '.format(
                job_id))
        message['To'] = email
        message['From'] = 'information@adnet.app'
        message['Subject'] = 'Job Error'

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

def gmail_send_error_admin(service, email, job_id, error):
    try:
        message = EmailMessage()
        message.set_content(
            'A job with ID {} has encountered an error. Further details should be provided to {} when the error has been handled. \n\n {}'
                .format(job_id, email, error))
        message['To'] = 'acretan@adnet.app'
        message['From'] = 'information@adnet.app'
        message['Subject'] = 'Job Error'

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


def gmail_verify(service, email, password):
    try:
        message = EmailMessage()
        message.set_content(
            'Your account with AdNet has been created! Please sign in at adnet.app and change your password using the auto-generated password below:\n\nPassword: {}\n\nThanks!'.format(
                password))
        message['To'] = email
        message['From'] = 'information@adnet.app'
        message['Subject'] = 'Account Creation'

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


def change_password(request):
    new_password = request.POST.get('new')
    username = request.POST.get('username')
    old_password = request.POST.get('old')

    if not username:
        username = request.user.email
    u = User.objects.get(username=username)
    if not u.check_password(old_password):
        return HttpResponse({'invalid_password'})
    if new_password == old_password:
        return HttpResponse({'duplicate_password'})
    conn = get_mongo()
    doc = conn.AdNet.users.find_one({'id': username})
    if doc['status'] == 'first_time':
        conn.AdNet.users.update_one({'id': username}, {"$set": {'status': 'unverified'}})
        u.set_password(new_password)
        u.save()

        return HttpResponse({'first_time'})
    else:
        u.set_password(new_password)
        u.save()
        return HttpResponse({'success': True})

def update_jobs(all_jobs, job_id, status):
    next_job = None
    for job in all_jobs:
        if job['name'] == job_id:
            job['status'] = status
        if job['name'] != job_id and job['status'] == 'pending (1)' and not next_job:
            next_job = job
            job['status'] = 'running'
        if 'pending' in job['status']:
            num = int(job['status'].split('(')[1].split(')')[0])
            num -= 1
            job['status'] = 'pending ({})'.format(num)
    return all_jobs, next_job

@csrf_exempt
def process_error(request):
    """
    processes any jobs that encountered an error while running.
    revert job status back to draft,
    send email detailing error information to admin, and email detailing
    that an error did occur to user

    :param request:
    :return:
    """
    data = json.loads(request.body)
    conn = get_mongo()
    all_jobs = conn.AdNet.users.find_one({'id': data['email']}, {'_id': 0, 'jobs': 1})['jobs']
    all_jobs, next_job = update_jobs(all_jobs, data['job_id'], 'draft')
    service = create_service()
    gmail_send_error_message(service, data['email'], data['job_id'])
    gmail_send_error_admin(service, data['email'], data['job_id'], data['error'])
    conn.AdNet.users.update_one({'id': data['email']}, {"$set": {'jobs': all_jobs}})
    if next_job:
        new_data = next_job
        new_data['user_id'] = data['email']
        url = BUILD_URL
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }
        requests.post(url, json=new_data, headers=headers)
    return HttpResponse({'success': True})

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

    data = json.loads(request.body)
    conn = get_mongo()
    all_jobs = conn.AdNet.users.find_one({'id': data['email']}, {'_id': 0, 'jobs': 1})['jobs']
    all_jobs, next_job = update_jobs(all_jobs, data['job_id'], 'completed')
    conn.AdNet.users.update_one({'id': data['email']}, {"$set": {'jobs': all_jobs}})
    service = create_service()
    gmail_send_message(service, data['email'], data['job_id'])
    if next_job:
        new_data = next_job
        new_data['user_id'] = data['email']
        url = BUILD_URL
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }
        requests.post(url, json=new_data, headers=headers)
    return HttpResponse({'success': True})
