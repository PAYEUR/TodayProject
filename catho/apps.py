from django.apps import AppConfig
from core.models import Topic
from .models import EventType


class CathoConfig(AppConfig):
    name = 'catho'


TOPIC = Topic.objects.get(name=CathoConfig.name)
EVENT_TYPE_LIST = EventType.objects.filter(topic=TOPIC)