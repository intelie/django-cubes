# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns(
    '',
    url(r'^', include('django_cubes.urls')),
)
