from django.conf.urls import url

from . import views

app_name = 'not_implemented'
urlpatterns = [
    url(r'^oooups$', views.NotImplementedView.as_view(), name="not_implemented"),
    ]