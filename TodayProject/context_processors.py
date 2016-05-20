# coding = utf8
from django.shortcuts import get_list_or_404
from topic.models import EventType
from core.models import Topic


def topic_sidebar():
    return {'topic_sidebar':  get_list_or_404(EventType)}


def core_sidebar():
    return {'core_sidebar':  get_list_or_404(Topic)}
