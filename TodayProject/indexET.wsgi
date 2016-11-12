"""
WSGI config for TodayProject project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os
import sys
import site

# Add the site-packages of the chosen virtualenv to work with
site.addsitedir('/var/www/todayproject/env/lib/python2.7/site-packages')

sys.path.append('/var/www/todayproject')
sys.path.append('/var/www/todayproject/Todayproject')

os.environ["DJANGO_SETTINGS_MODULE"] = "TodayProject.index_settings"

# Activate your virtual env
activate_env=os.path.expanduser("/var/www/todayproject/env/bin/activate_this.py")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

#import django.core.handlers.wsgi
#application = django.core.handlers.wsgi.WSGIHandler()
