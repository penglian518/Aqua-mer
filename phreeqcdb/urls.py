from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^master/$', views.master, name='master'),
    url(r'^species/$', views.species, name='species'),
    url(r'^phases/$', views.phases, name='phases'),
    url(r'^surfacemaster/$', views.surfacemaster, name='surfacemaster'),
    url(r'^surfacespecies/$', views.surfacespecies, name='surfacespecies'),
    url(r'^exchangemaster/$', views.exchangemaster, name='exchangemaster'),
    url(r'^exchangespecies/$', views.exchangespecies, name='exchangespecies'),
    url(r'^rates/$', views.rates, name='rates'),

]
