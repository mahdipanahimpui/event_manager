# Generated by Django 5.0.1 on 2024-05-21 13:30

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0005_participant_num_alter_meeting_participants_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='documents/')),
            ],
        ),
        migrations.AlterField(
            model_name='participant',
            name='mobile_phone_number',
            field=models.CharField(max_length=15, validators=[django.core.validators.RegexValidator(message='Phone number must be digits. (+) can be at first', regex='^[+]?[0-9]*$')]),
        ),
    ]
