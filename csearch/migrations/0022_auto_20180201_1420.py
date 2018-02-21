# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2018-02-01 19:20
from __future__ import unicode_literals

import csearch.models
import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('csearch', '0021_auto_20180201_1213'),
    ]

    operations = [
        migrations.AlterField(
            model_name='csearchjob',
            name='CreatedDate',
            field=models.DateTimeField(default=datetime.datetime(2018, 2, 1, 14, 20, 41, 689926), verbose_name='date created'),
        ),
        migrations.AlterField(
            model_name='csearchjob',
            name='UploadedFile',
            field=models.FileField(upload_to=csearch.models.user_directory_path),
        ),
    ]
