# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-06-25 01:34
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campaign', '0009_auto_20160618_2353'),
    ]

    operations = [
        migrations.AlterField(
            model_name='revenuereport',
            name='amount',
            field=models.DecimalField(decimal_places=2, help_text='The amount of revenue generated (in dollars) being reported (since last report)', max_digits=9),
        ),
    ]
