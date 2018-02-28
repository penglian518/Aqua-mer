from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^master/$', views.master, name='master'),
    url(r'^species/$', views.species, name='species'),
]
