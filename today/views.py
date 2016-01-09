from django.shortcuts import render
from django.http import HttpResponseRedirect

from .forms import NameForm


def index(request):
    return render(request, 'today/home.html')


def get_name(request):
    if request.method == 'POST':
        form = NameForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect('/today/')
    else:
        form = NameForm()

    return render(request, 'today/form.html', {'form': form})

