from django.urls import path, re_path
from webapp.SNPSearch import views

urlpatterns = [
	path('', views.index),
	path('GetAllSNPs/', views.get_all_snps),
	path('GetAllSNPNames/', views.get_all_names),
	re_path('GetSNPInfo/.*$', views.get_snp_data),
	re_path(r'get_details/.*$', views.get_snp_details),




]