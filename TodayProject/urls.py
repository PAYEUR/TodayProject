"""TodayProject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""

from django.conf.urls import include, url, static
from django.contrib import admin
from django.conf import settings


urlpatterns = [
    url(r'^', include('core.urls')),
    url(r'^connexion/', include('connection.urls')),
    url(r'^admin/', admin.site.urls),
    #the following namespaces have to be the same as topic.names in core.models.topic
    url(r'^catho/', include('topic.urls', namespace='catho')),
    url(r'^jobs/', include('topic.urls', namespace='jobs')),
    url(r'^', include('not_implemented.urls')),


    # media images deployment in development. Need change for production
    ]  + static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
