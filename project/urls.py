"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from .app import views
from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^$',
        views.home,
        name='home'),
    url(r'^about$',
        views.about,
        name='about'),
    url(r'^admin/', include(admin.site.urls)),
    # Client
    url(r'^client/(?P<pk>\d+)$',
        views.client,
        name='client'),
    url(r'^client/(?P<pk>\d+)/edit$',
        views.client_edit,
        name='client_edit'),
    url(r'^client/add$',
        views.client_edit,
        name='client_edit'),
    # Invoice
    url(r'^invoice/(?P<pk>\d+)$',
        views.invoice,
        name='invoice'),
    url(r'^invoice/(?P<pk>\d+)/edit$',
        views.invoice_edit,
        name='invoice_edit'),
    url(r'^invoice/add$',
        views.invoice_edit,
        name='invoice_edit'),
    url(r'^invoice/add\?client=(?P<client>\d+)$',
        views.invoice_edit,
        name='invoice_edit'),
    url(r'^invoice$',
        views.invoice_index,
        name='invoice_index'),
    # Project
    url(r'^project/(?P<pk>\d+)$',
        views.project,
        name='project'),
    url(r'^project/(?P<pk>\d+)/edit$',
        views.project_edit,
        name='project_edit'),
    url(r'^project/add$',
        views.project_edit,
        name='project_edit'),
    url(r'^project/add\?client=(?P<client>\d+)$',
        views.project_edit,
        name='project_edit'),
    url(r'^project$',
        views.project_index,
        name='project_index'),
    # Task
    url(r'^task/(?P<pk>\d+)$',
        views.task,
        name='task'),
    url(r'^task/(?P<pk>\d+)/edit$',
        views.task_edit,
        name='task_edit'),
    url(r'^task/add$',
        views.task_edit,
        name='task_edit'),
    url(r'^task/add\?project=(?P<project>\d+)$',
        views.task_edit,
        name='task_edit'),
    url(r'^task$',
        views.task_index,
        name='task_index'),
    url(r'^contact$',
        views.contact,
        name='contact'),
]
