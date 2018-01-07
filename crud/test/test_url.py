from django.conf.urls import url

from . import test_views
app_name = 'crud'
urlpatterns = [
    url(r'^two_event_types_test$', test_views.two_event_types_test, name="test1"),
    url(r'^occurrences_test$', test_views.occurrences_test, name="test2"),
    url(r'^occurrences_as_formset_test$', test_views.test_occurrences_as_formset, name="test3"),
    url(r'^test_add$', test_views.add_event_test, name="test4"),
    ]
