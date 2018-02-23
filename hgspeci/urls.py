from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    #url(r'^parameters/(?P<JobID>[0-9]+)/$', views.parameters_input, name='parameters_input'),
    url(r'^parameters/$', views.parameters, name='parameters'),
    url(r'^parameters/(?P<JobID>[0-9]+)/$', views.parameters_input, name='parameters_input'),
    url(r'^input_masterspecies/(?P<JobID>[0-9]+)/$', views.input_masterspecies, name='input_masterspecies'),
    url(r'^input_solutionspecies/(?P<JobID>[0-9]+)/$', views.input_solutionspecies, name='input_solutionspecies'),
    url(r'^ajax/query_solutionmaster/(?P<ele>.*)/$', views.query_solutionmaster, name='query_solutionmaster'),
    url(r'^ajax/query_solutionspecies/(?P<ele>.*)/$', views.query_solutionspecies, name='query_solutionspecies'),
    url(r'^review/(?P<JobID>[0-9]+)/$', views.review, name='review'),
    url(r'^review/$', views.review_doc, name='review_doc'),
    url(r'^results/(?P<JobID>[0-9]+)$', views.results, name='results'),
    url(r'^results/$', views.results_doc, name='results_doc'),
    url(r'^download/(?P<JobID>[0-9]+)$', views.download, name='download'),

]
