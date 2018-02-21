from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    #url(r'^parameters/(?P<JobID>[0-9]+)/$', views.parameters_input, name='parameters_input'),
    url(r'^parameters/$', views.parameters_input, name='parameters_input'),
    url(r'^ajax/query_solutionmaster/(?P<ele>.*)/$', views.query_solutionmaster, name='query_solutionmaster'),
    url(r'^ajax/query_solutionspecies/(?P<ele>.*)/$', views.query_solutionspecies, name='query_solutionspecies'),

]
