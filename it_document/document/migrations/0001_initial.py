# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-25 02:01
from __future__ import unicode_literals

import autoslug.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('category', '0002_auto_20170725_0820'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, unique=True)),
                ('level', models.CharField(max_length=50)),
                ('author', models.CharField(max_length=50)),
                ('submit_date', models.DateField(auto_now_add=True)),
                ('edited_date', models.DateField(auto_now=True)),
                ('link', models.URLField(blank=True, null=True)),
                ('image', models.ImageField(default='/document_images/question_mark.jpg', upload_to='document_images')),
                ('review', models.TextField()),
                ('number_of_likes', models.PositiveIntegerField(default=0)),
                ('number_of_views', models.PositiveIntegerField(default=0)),
                ('approve', models.BooleanField(default=False)),
                ('slug', autoslug.fields.AutoSlugField(editable=False, populate_from='title')),
                ('posted_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('topic', models.ManyToManyField(to='category.Category')),
            ],
        ),
    ]