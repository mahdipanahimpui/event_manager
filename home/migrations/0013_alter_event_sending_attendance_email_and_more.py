# Generated by Django 5.0.1 on 2024-05-27 12:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0012_rename_sending_attendansend_surveysce_email_event_sending_attendance_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='sending_attendance_email',
            field=models.BooleanField(),
        ),
        migrations.AlterField(
            model_name='meeting',
            name='sending_attendance_email',
            field=models.BooleanField(),
        ),
    ]
