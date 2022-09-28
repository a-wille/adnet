from django.shortcuts import redirect

def index(request):
	#redirects user to client url
	return redirect('/client/')
