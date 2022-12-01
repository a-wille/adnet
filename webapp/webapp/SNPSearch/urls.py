from django.urls import path
from webapp.SNPSearch import views

urlpatterns = [
	path('', views.index),
	path('GetAllSNPs/', views.get_all_snps),
	path('GetSNPData/', views.get_snp_data)
]