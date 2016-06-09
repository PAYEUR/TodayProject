# coding = utf8
from catho.models import EventType
from core.models import Topic
from django.shortcuts import get_object_or_404
from django.views.generic.list import MultipleObjectMixin
from django.views.generic import ListView

#def topic_sidebar(request):
    #return {'topic_sidebar':  EventType.objects.all()}


def core_sidebar(request):
    return {'core_sidebar':  Topic.objects.all()}


#class EventTypeList(ListView):
   # """class that gives the topic and the corresponding event_type_list and add them to the context"""

    #def get_queryset(self):
    #    self.topic = get_object_or_404(Topic, name=self.kwargs['topic_name'])
    #    return EventType.objects.filter(topic=self.topic)

    #def get_context_data(self, **kwargs):
       # context = super(EventTypeList, self).get_context_data(**kwargs)
        #context['topic'] = self.topic
       # context['event_type_list'] = self.get_queryset()


#def topic_sidebar(request):
    #context = {}
    #if request.kwargs['topic_name']:
      #  topic = get_object_or_404(Topic, name=request.kwargs['topic_name'])
     #   context['topic'] = topic
      #  context['topic_sidebar'] = EventType.objects.filter(topic=topic)

    #return context
