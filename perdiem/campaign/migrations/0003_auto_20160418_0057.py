# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-18 00:57
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campaign', '0002_auto_20160411_0246'),
    ]

    operations = [
        migrations.AlterField(
            model_name='investment',
            name='num_shares',
            field=models.PositiveSmallIntegerField(default=1, help_text='The number of shares an investor made in a transaction'),
        ),
    ]
