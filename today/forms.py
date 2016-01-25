from django.forms import CharField, Form, ModelForm
from swingtime import forms as fo
from today.models import EventWithImage


class NameForm(Form):
    """ formulaire bateau
    """
    your_name = CharField(label='Your name', max_length=100)


# Reverse url may be here?
class EventWithImageForm(fo.EventForm):
    class Meta():
        model = EventWithImage
        fields = '__all__'

