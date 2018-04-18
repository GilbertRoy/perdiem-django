# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-17 05:21
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('artist', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='artist',
            name='slug',
            field=models.SlugField(help_text='A short label for an artist (used in URLs)', max_length=40, unique=True),
        ),
    ]
