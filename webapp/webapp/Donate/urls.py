from django.urls import path
from . import views

urlpatterns = [
	path('GetAllEvents/', views.get_all_events),
	path('GetMyDonations/', views.get_my_donations)
]