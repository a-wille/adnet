from django.urls import path
from webapp.SNPSearch import views

urlpatterns = [
	path('', views.index),
	path('GetAllSNPs/', views.get_all_snps),
	path('GetAllSNPNames/', views.get_all_names),
	path('GetSNPData/', views.get_snp_data)
]