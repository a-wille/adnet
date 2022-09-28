from django.urls import path
from . import views

urlpatterns = [
	path('GetEvents/', views.get_volunteer_events),
	path('ViewActive/', views.get_active),
	path('ViewInActive/', views.get_inactive),
	path('Deactivate/', views.deactivate),
	path('Activate/', views.activate),
	path('GetAllEvents/', views.get_all_events),
	path('SignUp/', views.sign_up),
	path('Cancel/', views.cancel)
]