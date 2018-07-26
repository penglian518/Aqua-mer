from django.conf.urls import url
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^upload$', views.upload, name='upload'),
    url(r'^smiles$', views.smiles, name='smiles'),
    url(r'^draw$', views.draw, name='draw'),
    #url(r'^draw', TemplateView.as_view(template_name="csearch/draw.html"), name='draw'),
    url(r'^inputcoor/(?P<JobID>[0-9]+)/$', views.inputcoor, name='inputcoor'),
    url(r'^parameters/(?P<JobID>[0-9]+)/$', views.parameters_cstype, name='parameters_cstype'),
    url(r'^parameters_random/(?P<JobID>[0-9]+)/$', views.parameters_random, name='parameters_random'),
    url(r'^parameters_replica/(?P<JobID>[0-9]+)/$', views.parameters_replica, name='parameters_replica'),
    url(r'^parameters_dft/(?P<JobID>[0-9]+)/$', views.parameters_dft, name='parameters_dft'),
    url(r'^parameters/$', views.parameters, name='parameters'),
    url(r'^review/(?P<JobID>[0-9]+)/$', views.review, name='review'),
    url(r'^review/$', views.review_doc, name='review_doc'),
    url(r'^results/(?P<JobID>[0-9]+)$', views.results, name='results'),
    url(r'^results/(?P<JobID>[0-9]+)/xyz/(?P<Ith>[0-9]+)$', views.results_xyz, name='results_xyz'),
    url(r'^results/(?P<JobID>[0-9]+)/pdb/(?P<Ith>[0-9]+)$', views.results_pdb, name='results_pdb'),
    url(r'^results/$', views.results_doc, name='results_doc'),
    url(r'^reclustering/(?P<JobID>[0-9]+)$', views.reclustering, name='reclustering'),
    url(r'^reclustering/$', views.reclustering_doc, name='reclustering_doc'),
    url(r'^download/(?P<JobID>[0-9]+)$', views.download, name='download'),

]
