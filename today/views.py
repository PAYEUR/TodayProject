from django.shortcuts import render
from django.http import HttpResponseRedirect

from .forms import NameForm, PictureForm


def index(request):
    return render(request, 'today/home.html')


def base(request):
    return render(request, 'today/base.html')


def get_name(request):
    if request.method == 'POST':
        form = NameForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect('/today/')
    else:
        form = NameForm()

    return render(request, 'today/form.html', {'form': form})


def get_event(request):
    """
    non valid method
    :param request:
    :return:
    """
    if request.method == 'POST':
        form = PictureForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect('/today/')
    else:
        form = PictureForm()

    return render(request, 'today/form.html', {'form': form})
