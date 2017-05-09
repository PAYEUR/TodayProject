from django.http import HttpResponse

def index(request, city_slug):
    return HttpResponse("Vous etes a " + str(city_slug))