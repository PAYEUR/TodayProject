# coding="utf-8"
from django.conf.urls import url, include
import views

app_name = 'location'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<topic_name>[\w-]+)/', include('topic.urls')),
    #url(r'^not-implemented', include('not_implemented.urls')),
    ]
