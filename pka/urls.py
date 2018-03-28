from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^upload/(?P<Mol>.*)/(?P<JobID>.*)/$', views.upload, name='upload'),
    url(r'^start/$', views.start, name='start'),
    url(r'^smiles/(?P<JobID>[0-9]+)/$', views.smiles, name='smiles'),
    url(r'^inputcoor/(?P<JobID>[0-9]+)/(?P<Mol>.*)/$', views.inputcoor, name='inputcoor'),
    url(r'^inputfile/(?P<JobID>[0-9]+)/(?P<Mol>.*)/$', views.inputfile, name='inputfile'),

    url(r'^parameters/(?P<JobID>[0-9]+)/$', views.parameters_input, name='parameters_input'),
    url(r'^parameters/$', views.parameters, name='parameters'),

    url(r'^review/(?P<JobID>[0-9]+)/$', views.review, name='review'),
    url(r'^review/$', views.review_doc, name='review_doc'),
    url(r'^results/(?P<JobID>[0-9]+)$', views.results, name='results'),
    url(r'^results/(?P<JobID>[0-9]+)/xyz/(?P<Ith>[0-9]+)$', views.results_xyz, name='results_xyz'),
    url(r'^results/$', views.results_doc, name='results_doc'),

    url(r'^ajax/query_coor/(?P<JobID>.*)/$', views.query_coor, name='query_coor'),

]
