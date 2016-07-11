# coding = utf8
from topic.models import EventType
from core.models import Topic
from django.shortcuts import get_object_or_404

#from django.contrib.sites.models import Site

def topic_list(request):
    return {'topic_list':  Topic.objects.all()}


def topic_sidebar(request):
    """
    :param request: search the mother_namespace
    :return: add topic and topic_sidebar to the context depending on the called namaspace
    """

    # TODO mix this with core.utils.get_current_topic function
    mother_namespace = request.resolver_match.namespaces[0]
    topic_names = [topic.name for topic in Topic.objects.all()]
    context = dict()
    # print mother_namespace
    # print topic_names
    if mother_namespace in topic_names:
        topic = get_object_or_404(Topic, name=mother_namespace)
        context['topic'] = topic
        context['other_topics'] = Topic.objects.exclude(name=mother_namespace)
        context['topic_event_type_list'] = EventType.objects.filter(topic=topic)
    return context
