# coding = utf8
from topic.models import EventType
from core.models import Topic
from django.shortcuts import get_object_or_404


def core_sidebar(request):
    return {'core_sidebar':  Topic.objects.all()}


def topic_sidebar(request):
    """
    :param request: search the mother_namespace
    :return: add topic and topic_sidebar to the context depending on the called namaspace
    """
    mother_namespace = request.resolver_match.namespaces[0]
    topic_names = [topic.name for topic in Topic.objects.all()]
    context = dict()
    # print mother_namespace
    # print topic_names
    if mother_namespace in topic_names:
        topic = get_object_or_404(Topic, name=mother_namespace)
        context['topic'] = topic
        context['topic_sidebar'] = EventType.objects.filter(topic=topic)
    return context
