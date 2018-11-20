# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

from forms import ConnexionForm, MyUserCreationForm
from models import EnjoyTodayUser


def connexion(request):

    error = False
    if request.method == "POST":
        connexion_form = ConnexionForm(request.POST)
        if connexion_form.is_valid():
            username = connexion_form.cleaned_data["username"]
            password = connexion_form.cleaned_data["password"]
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                try:
                    request.GET.get('next')
                    return redirect(request.GET.get('next'))
                except TypeError:
                    return render(request, 'connection/logging_success.html')

            else:
                error = True

    else:
        connexion_form = ConnexionForm()

    context = dict({'connexion_form': connexion_form,
                    'error': error
                    })

    return render(request, 'connection/login.html', context)


@login_required()
def deconnexion(request):
    logout(request)
    return redirect('core:index')


def create_user(
        request,
        template='connection/inscription.html',
        form_class=MyUserCreationForm,
        ):

    logout(request)

    if request.method == 'POST':
        registration_form = form_class(request.POST)
        if registration_form.is_valid():
            registration_form.save()
            user = authenticate(password=registration_form.cleaned_data['password1'],
                                username=registration_form.cleaned_data['username'],
                                email=registration_form.cleaned_data['email']
                                )
            login(request, user)
            event_planner = EnjoyTodayUser(user=user)
            event_planner.save()
            return render(request, 'connection/logging_success.html')

    else:
        registration_form = form_class()

    context = dict({'registration_form': registration_form},
                   )

    return render(request, template, context)
