# Generated by Django 3.0.2 on 2020-02-25 08:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0006_user_company'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='sms_count',
            field=models.IntegerField(default=5),
        ),
    ]