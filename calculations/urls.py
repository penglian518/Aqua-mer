from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^level/(?P<level>[a-zA-Z0-9()-_+]+)/$', views.onelevel, name='onelevel'),
    url(r'^plot/(?P<logk_pair>[a-zA-Z0-9()-_+]+)/$', views.plotlogk, name='plotlogk'),
    url(r'^reactiongroup/(?P<level>[a-zA-Z0-9()-_+]+)/(?P<reaction_group>[a-zA-Z0-9()-_+]+)/$', views.onereactiongroup, name='onereactiongroup'),

]
