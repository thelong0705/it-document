# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-25 01:20
from __future__ import unicode_literals

import autoslug.fields
from django.db import migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('category', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='slug',
            field=autoslug.fields.AutoSlugField(default=django.utils.timezone.now, editable=False, populate_from='name'),
            preserve_default=False,
        ),
    ]
