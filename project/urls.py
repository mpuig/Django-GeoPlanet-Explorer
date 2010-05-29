from django.conf.urls.defaults import *
from django.conf import settings
import os

urlpatterns = patterns('app.views',
     url(r'^search/(?P<query>.+)$', 'search', name='search'),
     url(r'^search/$', 'search_form', name='search_form'),
     url(r'^woeid/(\d+)/(\w+)/$', 'woeid_collection', name='woeid_collection'),
     url(r'^woeid/(\d+)/$', 'woeid', name='woeid'),
     url(r'^$', 'home', name='home'),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.join(settings.PROJECT_PATH, 'static') }),
    )