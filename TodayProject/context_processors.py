# coding = utf8
from django.shortcuts import get_list_or_404
from topic.models import EventType
from core.models import Topic


def topic_sidebar(request):
    return {'topic_sidebar':  EventType.objects.all()}


def core_sidebar(request):
    return {'core_sidebar':  Topic.objects.all()}
