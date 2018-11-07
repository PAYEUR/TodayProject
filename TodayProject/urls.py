"""TodayProject URL Configuration for development environment
"""

from .prod_urls import urlpatterns as prod_url_patterns
from django.conf.urls import static, include, url
from django.conf import settings

test_url_patterns = [
    url(r'test-update', include('update_external_events'))
]

urlpatterns = test_url_patterns \
              + prod_url_patterns \
              + static.static(settings.MEDIA_URL,
                              document_root=settings.MEDIA_ROOT)
