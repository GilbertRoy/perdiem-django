# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-31 04:46
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('emails', '0002_auto_20160502_0538'),
    ]

    operations = [
        migrations.CreateModel(
            name='VerifiedEmail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('verified', models.BooleanField(default=False)),
                ('code', models.UUIDField(db_index=True, default=uuid.uuid4, unique=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterField(
            model_name='emailsubscription',
            name='subscription',
            field=models.CharField(choices=[('ALL', 'General'), ('NEWS', 'Newsletter'), ('ARTUP', 'Artist Updates')], default='ALL', max_length=6),
        ),
    ]
