# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2018-02-14 17:10
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Refs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('RefID', models.CharField(blank=True, max_length=20, null=True, unique=True)),
                ('Reference', models.CharField(blank=True, max_length=500, null=True, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='SolutionMasterSpecies',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Element', models.CharField(blank=True, default='', max_length=20)),
                ('Species', models.CharField(blank=True, default='', max_length=20)),
                ('Alkalinity', models.FloatField(blank=True, default=0.0)),
                ('GFWorFormula', models.CharField(blank=True, default='0', max_length=20)),
                ('GFWforElement', models.FloatField(blank=True, default=0.0)),
                ('Note', models.CharField(blank=True, default='', max_length=200)),
                ('CreatedDate', models.DateTimeField(default=datetime.datetime(2018, 2, 14, 12, 10, 13, 318914), verbose_name='date created')),
                ('Ref', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='phreeqcdb.Refs')),
            ],
        ),
    ]
