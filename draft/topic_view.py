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