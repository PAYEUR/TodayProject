from django import forms

class CalendarWidget(forms.TextInput):
    class Media:
        js = ('calendar.js')