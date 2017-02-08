from django.contrib import admin
from .models import City


class ArticleAdmin(admin.ModelAdmin):
    prepopulated_fields = {"city_slug": ("city_name",)}


admin.site.register(City)
