# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-20 07:24
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import gfklookupwidget.fields


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('music', '0005_auto_20160911_0829'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActivityEstimate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('activity_type', models.CharField(choices=[('stream', 'Stream'), ('download', 'Download')], max_length=8)),
                ('object_id', gfklookupwidget.fields.GfkLookupField()),
                ('total', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='contenttypes.ContentType')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='activityestimate',
            unique_together=set([('date', 'activity_type', 'content_type', 'object_id')]),
        ),
    ]
