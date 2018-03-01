# coding = utf8
from topic.models import Topic
from location.models import City
from django.core.urlresolvers import resolve


def topic_list(request):
    return {'topic_list': Topic.objects.all()}


def cities_list(request):
    return {'cities': City.objects.all()}
