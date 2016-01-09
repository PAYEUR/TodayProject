from django.forms import CharField, Form, ModelForm
from today.models import Picture


class PictureForm(ModelForm):
    class Meta:
        model = Picture
        fields = '__all__'


class NameForm(Form):
    """ formulaire bateau
    """
    your_name = CharField(label='Your name', max_length=100)