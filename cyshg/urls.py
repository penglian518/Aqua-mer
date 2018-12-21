"""cyshg URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from . import views


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^faq/', views.faq, name='faq'),
    url(r'^ajax/query_statistics/$', views.query_statistics, name='query_statistics'),

    url(r'^toolkit/', include('toolkit.urls')),
    url(r'^expdata/', include('expdata.urls')),
    url(r'^calcdata/', include('calcdata.urls')),
    url(r'^Cal/', include('calculations.urls')),
    url(r'^csearch/', include('csearch.urls')),
    url(r'^gsolv/', include('gsolv.urls')),
    url(r'^pka/', include('pka.urls')),
    url(r'^logk/', include('logk.urls')),
    url(r'^hgspeci/', include('hgspeci.urls')),
    url(r'^phreeqcdb/', include('phreeqcdb.urls')),
    url(r'^admin/', admin.site.urls),
]
