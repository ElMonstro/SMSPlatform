# Generated by Django 3.0.2 on 2020-03-19 21:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sms', '0012_auto_20200318_2343'),
    ]

    operations = [
        migrations.RenameField(
            model_name='emailrequest',
            old_name='sms_count',
            new_name='email_count',
        ),
    ]
