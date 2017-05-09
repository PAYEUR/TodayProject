from topic.models import Topic
from django.shortcuts import get_object_or_404, redirect
from topic.views import index2


def index(request, city_slug):

    #TODO : overwrite spi when not only spi events
    spi = get_object_or_404(Topic, name='spi')
    return redirect('location:topic:index',
                    city_slug = city_slug,
                    topic_name = spi.name,
                    )