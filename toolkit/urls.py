from django.conf.urls import url
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^upload$', views.upload, name='upload'),
    url(r'^smiles$', views.smiles, name='smiles'),
    url(r'^draw$', views.draw, name='draw'),
    url(r'^inputcoor/(?P<JobID>[0-9]+)/$', views.inputcoor, name='inputcoor'),
    url(r'^reviewcoors/(?P<JobID>[0-9]+)/$', views.reviewcoors, name='reviewcoors'),
    url(r'^trans/(?P<JobType>.*)/(?P<JobID>[0-9]+)/$', views.trans, name='trans'),

]
