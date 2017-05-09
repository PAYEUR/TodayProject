# coding=utf-8
#TODO: where is the mention of city here?
# vue initiale, remise ici pour memoire

def index2(request, topic_name, city_slug, template='topic/research.html'):
    """
    :param request:
    :param template:
    :return: home template with index form
    """

    context = dict()
    topic = get_object_or_404(Topic, name=topic_name)
    city = get_object_or_404(City, city_slug=city_slug)

    if request.method == 'POST':
        form = IndexForm(topic, request.POST)

        if form.is_valid():
            # required
            query_date = form.cleaned_data['quand']
            # blank allowed
            event_type_list = form.cleaned_data['quoi']
            # hour by default else.
            start_hour = form.cleaned_data['start_hour']
            end_hour = form.cleaned_data['end_hour']

            if event_type_list:
                event_type_id_string = utils.create_id_string(event_type_list)
            else:
                event_type_id_string = utils.create_id_string(EventType.objects.filter(topic=topic))

            return redirect(reverse('topic:single_time_event_type_list',
                                    kwargs={'year': query_date.year,
                                            'month': query_date.month,
                                            'day': query_date.day,
                                            'event_type_id_string': event_type_id_string,
                                            'start_hour_string': utils.construct_hour_string(start_hour),
                                            'end_hour_string': utils.construct_hour_string(end_hour),
                                            },
                                    )
                            )

    else:
        form = IndexForm(topic)

    context['form'] = form

    return render(request, template, context)




# another way to write it
# class LocationTopicList(ListView):
#
#     template = 'topic/sorted_events.html'
#     context_object_name = 'sorted_occurrences'
#
#     def get_queryset(self):
#         self.current_location = get_object_or_404(City, city_slug=self.kwargs['city_slug'])
#         self.topic = get_object_or_404(Topic, name=self.kwargs['topic_name'])
#         self.event_type_list = utils.get_event_type_list(self.kwargs['event_type_id_string'])
#
#         start_date = utils.construct_day(self.kwargs['start_year'], self.kwargs['start_month'], self.kwargs['start_day'])
#         start_hour = utils.construct_hour(self.kwargs['start_hour_string'])
#         self.start_time = utils.construct_time(start_date, start_hour)
#
#         end_date = utils.construct_day(self.kwargs['end_year'], self.kwargs['end_month'], self.kwargs['end_day'])
#         end_hour = utils.construct_hour(self.kwargs['end_hour_string'])
#         self.end_time = utils.construct_time(end_date, end_hour)
#
#         return Occurrence.objects.filter(event__location=self.current_location,
#                                          event__event_type__topic=self.topic,
#                                          event__event_type__in=self.event_type_list,
#                                          start_time__gte=self.start_time,
#                                          end_time__lte=self.end_time,
#                                          )
#
#     def get_context_data(self, **kwargs):
#         context = super(LocationTopicList, self).get_context_data(**kwargs)
#         context['days'] = utils.list_days(self.start_time, self.end_time)
#         context['title'] = ' - '.join([event.label for event in self.event_type_list])