from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^upload/(?P<JobID>.*)/$', views.upload, name='upload'),
    url(r'^start/(?P<type>.*)/$', views.start, name='start'),
    url(r'^smiles/(?P<JobID>[0-9]+)/$', views.smiles, name='smiles'),
    url(r'^inputcoor/(?P<JobID>[0-9]+)/(?P<Mol>.*)/$', views.inputcoor, name='inputcoor'),
    url(r'^inputfile/(?P<JobID>[0-9]+)/(?P<JobType>.*)/$', views.inputfile, name='inputfile'),
    url(r'^outputfile/(?P<JobID>[0-9]+)/(?P<Mol>.*)/$', views.outputfile, name='outputfile'),

    url(r'^parameters/(?P<JobID>[0-9]+)/$', views.parameters_input, name='parameters_input'),
    url(r'^parameters/$', views.parameters, name='parameters'),

    url(r'^review/(?P<JobID>[0-9]+)/$', views.review, name='review'),
    url(r'^review/$', views.review_doc, name='review_doc'),

    url(r'^results/(?P<JobID>[0-9]+)/(?P<JobType>.*)/$', views.results, name='results'),
    url(r'^results/(?P<JobID>[0-9]+)/xyz/(?P<Ith>[0-9]+)$', views.results_xyz, name='results_xyz'),
    url(r'^results/$', views.results_doc, name='results_doc'),

    url(r'^calculate/(?P<JobID>[0-9]+)/$', views.calculate, name='calculate'),
    url(r'^download/(?P<JobID>[0-9]+)$', views.download, name='download'),

]
