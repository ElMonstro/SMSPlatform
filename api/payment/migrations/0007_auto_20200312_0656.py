# Generated by Django 3.0.2 on 2020-03-12 06:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0006_auto_20200309_0956'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rechargeplan',
            name='name',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]