"""
WSGI config for TodayProject project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# leave blank in dev environment:
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "TodayProject.prod_settings")

application = get_wsgi_application()
