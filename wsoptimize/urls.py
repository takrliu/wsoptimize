from django.conf.urls import patterns, include, url
# from django.contrib import admin
from wsoptimize import views


urlpatterns = patterns('',
    url(r'^$', views.calculate_form, name='index'),
    url(r'^calculate$', views.calculate_form, name='calculate'),
    url(r'^display$', views.display, name='display'),
    url(r'^buffs$', views.buffs_form, name='buffs'),
    # (r'^display#$', views.displaygraph),
    # (r'^chart$', views.graph),
    # (r'/contact/$', view_contact_method, 'contact_url_name'),
)
