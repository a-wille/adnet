from django.urls import path, re_path
from . import views

urlpatterns = [
	path('', views.index),
	path('events', views.events),
	path('home', views.home),
	path('donate', views.donate),
	path('volunteer', views.volunteer),
	path('all_events', views.all_events),
	path('all_volunteers', views.all_volunteers),
	path('login', views.login),
	path('create', views.account_view),
	path('user_manual/', views.user_manual),
	path('donate_unrestricted', views.donation_unrestricted),
	re_path(r'donate_restricted/.*$', views.donation_restricted),
	re_path(r'user_summary/.*$', views.user_summary),
	path('make_restricted_donation/', views.make_restricted_donation),
	path('make_unrestricted_donation/', views.make_unrestricted_donation),
	path('check_login/', views.check_login),
	path('create_account/', views.create_account),
	path('logout/', views.my_logout),
	path('check_admin/', views.check_admin)
]


