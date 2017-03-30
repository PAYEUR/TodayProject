# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2017-03-30 14:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city_name', models.CharField(default='Paris', help_text='Nom de la ville', max_length=255, verbose_name='city_name')),
                ('city_slug', models.CharField(default='paris', help_text="Nom de la ville affich\xe9 dans l'url", max_length=255, verbose_name='city_slug')),
                ('city_big_map_coordinates', models.CharField(default='155,52,155,83,238,88,237,56', help_text='Coordonn\xe9es html de la zone de la grande carte de France correspondant \xe0 la ville, au format 155,52,155,83,238,88,237,56', max_length=255, verbose_name='city_big_map_coordinates')),
                ('city_small_map_coordinates', models.CharField(default='89,33,88,48,136,49,135,37', help_text='Coordonn\xe9es html de la zone de la petite carte de France correspondant \xe0 la ville, au format 155,52,155,83,238,88,237,56', max_length=255, verbose_name='city_small_map_coordinates')),
            ],
            options={
                'verbose_name': 'city',
                'verbose_name_plural': 'cities',
            },
        ),
    ]
