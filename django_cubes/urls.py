# -*- coding: utf-8 -*-
try:
    from django.conf.urls import patterns, url
except ImportError:
    from django.conf.urls.defaults import patterns, url

from .api import (
    ApiVersion, Index, Info, ListCubes,
    CubeModel, CubeAggregation, CubeCell,
    CubeReport, CubeFacts, CubeFact, CubeMembers
)

urlpatterns = patterns(
    '',
    url(r'^$', Index.as_view(), name='index'),
    url(r'^version/$', ApiVersion.as_view(), name='version'),
    url(r'^info/$', Info.as_view(), name='info'),
    url(r'^cubes/$', ListCubes.as_view(), name='cubes'),
    url(r'^cube/(?P<cube_name>\S+)/model/$', CubeModel.as_view(), name='cube_model'),
    url(r'^cube/(?P<cube_name>\S+)/aggregate/$', CubeAggregation.as_view(), name='cube_aggregation'),
    url(r'^cube/(?P<cube_name>\S+)/cell/$', CubeCell.as_view(), name='cube_cell'),
    url(r'^cube/(?P<cube_name>\S+)/report/$', CubeReport.as_view(), name='cube_report'),
    url(r'^cube/(?P<cube_name>\S+)/facts/$', CubeFacts.as_view(), name='cube_facts'),
    url(r'^cube/(?P<cube_name>\S+)/fact/(?P<fact_id>\S+)/$', CubeFact.as_view(), name='cube_fact'),
    url(r'^cube/(?P<cube_name>\S+)/members/(?P<dimension_name>\S+)/$', CubeMembers.as_view(), name='cube_members'),
)
