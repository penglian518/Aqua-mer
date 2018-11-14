from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^master/$', views.master, name='master'),
    url(r'^species/$', views.species, name='species'),
    url(r'^xyz/(?P<ID>[0-9]+)$', views.xyz, name='xyz'),
    url(r'^viewxyz/(?P<ID>[0-9]+)$', views.viewxyz, name='viewxyz'),
    url(r'^viewele/(?P<element>.*)/$', views.viewele, name='viewele'),
]
