# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2017-03-30 14:51
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('connection', '0001_initial'),
        ('location', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(default=None, help_text=b"image affich\xc3\xa9e pour l'\xc3\xa9v\xc3\xa9nement", upload_to=b'events/', verbose_name=b'Image')),
                ('title', models.CharField(default=None, help_text=b"Titre affich\xc3\xa9 pour l'\xc3\xa9v\xc3\xa9nement", max_length=100, verbose_name=b'Titre')),
                ('description', models.TextField(default=None, help_text=b"Description de l'\xc3\xa9v\xc3\xa9nement. Ajouter \xc3\xa9galement tout d\xc3\xa9tails utiles", verbose_name=b'Description')),
                ('price', models.CharField(blank=True, default=None, help_text=b'Conditions tarifaires', max_length=300, verbose_name=b'Prix')),
                ('contact', models.CharField(blank=True, default=None, help_text=b"Informations sur l'organisateur <u>officiel</u> de l'\xc3\xa9v\xc3\xa9nement", max_length=150, verbose_name=b'D\xc3\xa9tails organisateur')),
                ('address', models.CharField(default=None, help_text=b"Donner l'adresse postale <u>au sens de google</u>", max_length=150, verbose_name=b'Adresse')),
                ('public_transport', models.CharField(blank=True, default=None, help_text=b'Arr\xc3\xaat de m\xc3\xa9tro,...', max_length=150, verbose_name=b'Transport en commun')),
                ('created_at', models.DateTimeField(auto_now=True, verbose_name=b'Date de cr\xc3\xa9ation')),
                ('event_planner', models.ForeignKey(blank=True, default=None, on_delete=django.db.models.deletion.CASCADE, to='connection.EnjoyTodayUser', verbose_name=b'annonceur')),
            ],
            options={
                'ordering': ('title',),
                'verbose_name': 'event',
                'verbose_name_plural': 'events',
            },
        ),
        migrations.CreateModel(
            name='EventType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(default=b'autres', max_length=50, verbose_name=b'label')),
                ('image', models.ImageField(default=None, null=True, upload_to=b'event_types/')),
            ],
            options={
                'verbose_name': 'event type',
                'verbose_name_plural': 'event types',
            },
        ),
        migrations.CreateModel(
            name='Occurrence',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('is_multiple', models.BooleanField(default=False)),
                ('event', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to='topic.Event')),
            ],
            options={
                'ordering': ('start_time', 'end_time'),
                'verbose_name': 'occurrence',
                'verbose_name_plural': 'occurrences',
            },
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default=b'catho', max_length=50, verbose_name=b'Th\xc3\xa9matique')),
            ],
            options={
                'verbose_name': 'topic',
                'verbose_name_plural': 'topics',
            },
        ),
        migrations.AddField(
            model_name='eventtype',
            name='topic',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, to='topic.Topic', verbose_name=b'Thematique'),
        ),
        migrations.AddField(
            model_name='event',
            name='event_type',
            field=models.ForeignKey(default=None, help_text=b"Cat\xc3\xa9gorie \xc3\xa0 laquelle est rattach\xc3\xa9 l'\xc3\xa9v\xc3\xa9nement", on_delete=django.db.models.deletion.SET_DEFAULT, to='topic.EventType', verbose_name=b'Cat\xc3\xa9gorie'),
        ),
        migrations.AddField(
            model_name='event',
            name='location',
            field=models.ForeignKey(default=None, help_text=b"ville dans laquelle sera post\xc3\xa9 l'\xc3\xa9v\xc3\xa9nement", on_delete=django.db.models.deletion.SET_DEFAULT, to='location.City'),
        ),
    ]
