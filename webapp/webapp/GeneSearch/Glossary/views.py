from django.shortcuts import render


def index(request):
	"""returns home page"""
	return render(request, 'index.html')

