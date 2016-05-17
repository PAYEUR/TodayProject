# coding=utf-8

from __future__ import print_function, unicode_literals
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class ConnexionForm(forms.Form):
    username = forms.CharField(label="Login", max_length=30)
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)


class MyUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def save(self, commit=True):
        user = super(MyUserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
