from localdev_settings import *


#launch it with following code:
#  runserver --settings TodayProject.localdev_index_settings.p 127.0.0.1:8002

SITE_ID = 5

ALLOWED_HOSTS = ['127.0.0.1:8002']

ROOT_URLCONF = 'TodayProject.index_urls'
WSGI_APPLICATION = 'TodayProject.index_wsgi.application'