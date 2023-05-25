from django.urls import path, re_path
from webapp.GeneSearch import views

urlpatterns = [
	path('', views.index),
	path('GetAllGenes/', views.get_all_genes),
	path('GetAllGeneNames/', views.get_all_names),
	re_path('GetGeneInfo/.*$', views.get_gene_info),
	re_path(r'get_information/.*$', views.get_gene_details),
	re_path(r'.*$', views.gene_page)
]