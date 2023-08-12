from django.urls import path, re_path
from webapp.JobConfigurations import views

urlpatterns = [
	path('GetAllJobs/', views.get_all_jobs),
	path('GetCompletedJobs/', views.get_completed_jobs),
	path('Create/', views.create),
	path('Edit/', views.edit),
	path('Delete/', views.delete),
	path('AddToConfig/', views.add_item),
	path('GetAddJobs/', views.get_add_jobs),
	re_path(r'GetMLConfigurations/.*$', views.get_ml_configurations),
	re_path(r'GetMLForJob/.*$', views.get_ml_for_job),
	path('SetMLConfigs/', views.set_ml_configs)
]

