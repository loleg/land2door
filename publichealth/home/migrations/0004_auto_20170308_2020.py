# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-08 19:20
from __future__ import unicode_literals

from django.db import migrations
import wagtail.wagtailcore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_auto_20170223_0959'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='articlepage',
            name='date',
        ),
        migrations.AddField(
            model_name='articleindexpage',
            name='intro_de',
            field=wagtail.wagtailcore.fields.RichTextField(default=''),
        ),
        migrations.AddField(
            model_name='articleindexpage',
            name='intro_fr',
            field=wagtail.wagtailcore.fields.RichTextField(default=''),
        ),
    ]
