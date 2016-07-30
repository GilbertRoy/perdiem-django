# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-07-30 18:02
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0002_auto_20160725_0226'),
    ]

    operations = [
        migrations.CreateModel(
            name='AlbumBio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bio', models.TextField(help_text='Tracklisting and other info about the album. <a href="http://daringfireball.net/projects/markdown/syntax" target="_blank">Markdown syntax</a> allowed, but no raw HTML. Examples: **bold**, *italic*, indent 4 spaces for a code block.')),
            ],
        ),
        migrations.AddField(
            model_name='album',
            name='release_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='albumbio',
            name='album',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='music.Album'),
        ),
    ]
