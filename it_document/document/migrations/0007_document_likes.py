# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-27 06:49
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('document', '0006_document_level'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='likes',
            field=models.ManyToManyField(blank=True, related_name='liked_documents', to=settings.AUTH_USER_MODEL),
        ),
    ]
