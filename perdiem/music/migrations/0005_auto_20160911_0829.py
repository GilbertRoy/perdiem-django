# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-11 08:29
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0004_track'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='track',
            unique_together=set([('album', 'disc_number', 'track_number')]),
        ),
    ]
