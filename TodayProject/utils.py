from topic.models import Topic
from location.models import City
from django.shortcuts import get_object_or_404


def get_current_topic(request):
    """
    :return: gives the current topic
    for example, if the current url is www.mysite.fr/paris/spi returns spi
    but if the current url is www.mysite.fr/contact returns None
    """
    second_namespace = request.resolver_match.namespaces[1]
    topic_names = [topic.name for topic in Topic.objects.all()]
    if second_namespace in topic_names:
        return get_object_or_404(Topic, name=second_namespace)
    else:
        return None


# def get_current_city(request):
#     """
#     :return: gives the current topic
#     for example, if the current url is www.mysite.fr/paris/spi returns paris
#     but if the current url is www.mysite.fr/contact returns None
#     """
#     first_namespace = request.resolver_match.namespaces[0]
#     city_names = [city.city_name for city in City.objects.all()]
#     if first_namespace in city_names:
#         return get_object_or_404(City, name=first_namespace)
#     else:
#         return None
