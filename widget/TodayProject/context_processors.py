# coding = utf8
from topic.models import EventType
from core.models import Topic
from django.shortcuts import get_object_or_404
from core import utils


def topic_list(request):
    # modified to only take into account catho event
    return {'topic_list':  Topic.objects.filter(name__contains='catho')}


def topic_sidebar(request):
    """
    :param request: search the mother_namespace
    :return: add current_topic and current_topic_event_type_list to the context depending on the called namespace
    """

    # TODO mix this with core.utils.get_current_topic function
    mother_namespace = request.resolver_match.namespaces[0]
    topic_names = [topic.name for topic in Topic.objects.all()]
    context = dict()
    # print mother_namespace
    # print topic_names
    if mother_namespace in topic_names:
        current_topic = get_object_or_404(Topic, name=mother_namespace)
        context['current_topic'] = current_topic
        context['current_topic_event_type_list'] = EventType.objects.filter(topic=current_topic)
    return context


# TODO this is totally aweful and must be replaced by correct django.site implementation
def city_name(request):
    """
    returns name of subdomain expectig beeing name of the city
    for example if subdomain is paris.enjoytoday.fr, returns Paris
    """
    current_url = request.build_absolute_uri()
    a = current_url.split('//')[1]
    b = a.split('.')[0]
    return {'city_name' : b.title()}