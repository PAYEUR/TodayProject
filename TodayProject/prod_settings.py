"""
prod_settings
"""

from .settings import *

with open('/etc/enjoytoday_secret_key.txt') as f:
    SECRET_KEY = f.read().strip()

DEBUG = False

ROOT_URLCONF = 'TodayProject.prod_urls'

ALLOWED_HOSTS = ['enjoytoday.payeur.eu']
