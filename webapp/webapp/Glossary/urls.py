from django.urls import path, re_path
from . import views

urlpatterns = [
	path('', views.index),
    path('GetAllTerms/', views.get_all_terms),
    path('GetTermDefinition/', views.get_term_definition),
    path('GetMLTerms/', views.get_ml_terms),
    path('GetGTerms/', views.get_g_terms),
    re_path('.*', views.glossary_page)
]