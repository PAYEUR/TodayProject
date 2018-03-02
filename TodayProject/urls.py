"""TodayProject URL Configuration for development environment
"""

from .prod_urls import urlpatterns as prod_url_patterns
from django.conf.urls import static
from django.conf import settings


urlpatterns = prod_url_patterns + static.static(settings.MEDIA_URL,
                                                document_root=settings.MEDIA_ROOT)
