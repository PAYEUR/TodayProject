#from topic.models import Topic
#from location.models import City
#from django.shortcuts import get_object_or_404


# def get_city_and_topic(request):
#     arguments = request.get_full_path().split("/")
#     topic_names = [topic.name for topic in Topic.objects.all()]
#     city_slugs = [city.city_slug for city in City.objects.all()]
#
#     data = {'topic': None,
#             'city': None,
#             }
#
#     for arg in arguments:
#         if arg in topic_names:
#             data['topic'] = get_object_or_404(Topic, name=arg)
#         elif arg in city_slugs:
#             data['city'] = get_object_or_404(City, city_slug=arg)
#
#     return data
