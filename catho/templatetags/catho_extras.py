from core.models import Topic
from catho.models import EventType
from catho.apps import CathoConfig
from django import template

register = template.Library()

@register.simple_tag()
# TODO to be completed
def nav_bar():
    topic = Topic.objects.get(name=CathoConfig.name)
    event_type_list = EventType.objects.filter(topic=topic)
    return event_type_list
