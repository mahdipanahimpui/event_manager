# Generated by Django 5.0.1 on 2024-05-05 11:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Meeting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=100)),
                ('title', models.CharField(max_length=200)),
                ('holding_time', models.DateTimeField()),
                ('presenter', models.CharField(max_length=200)),
                ('about_presenter', models.TextField(blank=True, max_length=1000, null=True)),
                ('organizer', models.CharField(blank=True, max_length=200, null=True)),
                ('holding_place', models.TextField(max_length=500)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.event')),
                ('participants', models.ManyToManyField(blank=True, null=True, to='home.participant')),
            ],
        ),
    ]