from django.urls import path, re_path
from . import views

urlpatterns = [
	path('ViewAll/', views.get_all),
	path('ViewAllTime/', views.get_all_time),
	path('Edit/', views.edit),
	path('Create/', views.create),
	path('Delete/', views.delete),
	path('DeleteEvent/', views.delete_event),
	path('ViewCancelled/', views.get_cancelled),
	path('UncancelEvent/', views.uncancel_event),
	path('', views.index),
]
