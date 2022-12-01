from django.urls import path
from webapp.GeneSearch import views

urlpatterns = [
	path('', views.index),
	path('GetAllGenes/', views.get_all_genes),
	path('GetAllGeneNames/', views.get_all_names),
	path('GetGeneData/', views.get_gene_data)
]