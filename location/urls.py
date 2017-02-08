# coding="utf-8"
from django.conf.urls import url, include


app_name = 'location'
urlpatterns = [
    url(r'^(?P<topic_name>[\w-]+)/', include('topic.urls')),
    # url(r'^jobs/', include('topic.urls', namespace='jobs')),
    url(r'^not-implemented', include('not_implemented.urls')),
    ]
