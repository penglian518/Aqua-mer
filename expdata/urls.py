from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^basic/$', views.basic, name='basic'),
    url(r'^dgsolv/$', views.dgsolv, name='dgsolv'),
    url(r'^pka/$', views.pka, name='pka'),
    url(r'^stability/$', views.stability, name='stability'),
    url(r'^cpd/(?P<args>\w+)/(?P<value>[0-9]+)/$', views.onecpd, name='onecpd'),

]
