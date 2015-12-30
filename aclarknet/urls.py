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
from django.conf.urls import include
from django.conf.urls import url
from django.contrib import admin
from .database import views

urlpatterns = [
    url(r'^$',
        views.home,
        name='home'),
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
    url(r'^client$',
        views.client_index,
        name='client_index'),
    # Company
    url(r'^company/edit$',
        views.company_edit,
        name='company_edit'),
    url(r'^company$',
        views.company,
        name='company'),
    # Contact
    url(r'^contact/(?P<pk>\d+)$',
        views.contact,
        name='contact'),
    url(r'^contact/(?P<pk>\d+)/edit$',
        views.contact_edit,
        name='contact_edit'),
    url(r'^contact/add$',
        views.contact_edit,
        name='contact_edit'),
    url(r'^contact$',
        views.contact_index,
        name='contact_index'),
    # Estimate
    url(r'^estimate/(?P<pk>\d+)$',
        views.estimate,
        name='estimate'),
    url(r'^estimate/(?P<pk>\d+)/edit$',
        views.estimate_edit,
        name='estimate_edit'),
    url(r'^estimate/add$',
        views.estimate_edit,
        name='estimate_edit'),
    url(r'^estimate$',
        views.estimate_index,
        name='estimate_index'),
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
    url(r'^project$',
        views.project_index,
        name='project_index'),
    # Social
    url('',
        include('django.contrib.auth.urls',
                namespace='auth')),
    url('',
        include('social.apps.django_app.urls',
                namespace='social')),
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
    url(r'^task$',
        views.task_index,
        name='task_index'),
    # Time
    url(r'^time/(?P<pk>\d+)$',
        views.time,
        name='entry'),
    url(r'^time/(?P<pk>\d+)/edit$',
        views.time_edit,
        name='entry_edit'),
    url(r'^time/add$',
        views.time_edit,
        name='entry_edit'),
    url(r'^time$',
        views.time_index,
        name='entry_index'),
    # User
    url(r'^user/(?P<pk>\d+)$',
        views.user,
        name='user'),
    url(r'^user/(?P<pk>\d+)/edit$',
        views.user_edit,
        name='user_edit'),
    url(r'^user/(?P<pk>\d+)/mail$',
        views.user_mail,
        name='user_mail'),
    url(r'^user$',
        views.user_index,
        name='user_index'),
]
