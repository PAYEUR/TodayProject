# coding = utf8
from topic.models import Topic, EventType
from location.models import City
from . import utils


def topic_list(request):
    # modified to only take into account spi event
    return {'topic_list':  Topic.objects.filter(name__contains='spi')}


def cities_list(request):
    return {'cities': City.objects.all()}


# TODO remove this if unused
# def current_city(request):
#     return {'current_city': utils.get_city_and_topic(request)['city']}
#
#
# def topic_sidebar(request):
#     """
#     :param request: look for the current topic name from url
#     :return: add current_topic and current_topic_event_type_list to the context depending on the called namespace
#     """
#     context = dict()
#     current_topic = utils.get_city_and_topic(request)['topic']
#     context['current_topic'] = current_topic
#     context['current_topic_event_type_list'] = EventType.objects.filter(topic=current_topic)
#     return context
