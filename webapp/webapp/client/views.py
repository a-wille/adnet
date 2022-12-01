from django.shortcuts import render
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate, logout
from webapp.models import User
from django.contrib.auth import login as login_django
from webapp.extra.view_helper import get_mongo
from django.http import HttpResponse


def index(request):
	# returns index page
	return render(request, 'index.html')

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