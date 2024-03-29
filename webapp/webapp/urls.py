from django.contrib import admin
from django.conf import settings
from django.urls import path, include, re_path
from django.conf.urls.static import static
from webapp import views

urlpatterns = [
    # path('client/', include('webapp.client.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('Glossary/', include('webapp.Glossary.urls')),
    path('GeneSearch/', include('webapp.GeneSearch.urls')),
    path('SNPSearch/', include('webapp.SNPSearch.urls')),
    path('JobConfigurations/', include('webapp.JobConfigurations.urls')),
    path('', views.index),
    path('glossary', views.glossary),
	path('home', views.home),
	path('gene_search', views.gene_search),
	path('snp_search', views.snp_search),
	path('account_view', views.accounts_view),
	path('submit_job/', views.submit_job),
	path('process_results/', views.process_results),
	path('process_error/', views.process_error),
	path('change_password/', views.change_password),
	re_path('change_pass_window/.*$', views.get_change_pass_window),
	path('build', views.build),
	path('run', views.run),
	path('login', views.login),
	path('create', views.account_view),
	path('check_login/', views.check_login),
	path('create_account/', views.create_account),
	path('logout/', views.my_logout),
	path('check_admin/', views.check_admin),
	path('get_unverified_users/', views.get_unverified_users),
	path('delete_user/', views.delete_user),
	path('approve_user/', views.approve_user)
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

