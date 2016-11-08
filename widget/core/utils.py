from .models import Topic
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.contrib.sites.models import Site


def get_current_topic(request):
    """
    :return: gives the current topic
    for example, if the current url is www.mysite.fr/catho returns catho
    but if the current url is www.mysite.fr/nouvel_evenement returns None
    """
    mother_namespace = request.resolver_match.namespaces[0]
    topic_names = [topic.name for topic in Topic.objects.all()]
    if mother_namespace in topic_names:
        return get_object_or_404(Topic, name=mother_namespace)
    else:
        return None