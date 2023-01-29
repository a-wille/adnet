from django.urls import path, re_path, include
from . import views

urlpatterns = [
	path('', views.index),
	path('glossary', views.glossary),
	path('home', views.home),
	path('gene_search', views.gene_search),
	path('snp_search', views.snp_search),
	path('build', views.build),
	path('run', views.run),
	path('login', views.login),
	path('create', views.account_view),
	path('check_login/', views.check_login),
	path('create_account/', views.create_account),
	path('logout/', views.my_logout),
	path('check_admin/', views.check_admin)
]


