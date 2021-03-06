# Generated by Django 2.2.12 on 2020-05-15 03:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0008_auto_20200312_2323'),
    ]

    operations = [
        migrations.CreateModel(
            name='BrandingFee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fee', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
        migrations.AddField(
            model_name='rechargerequest',
            name='transaction_desc',
            field=models.CharField(default='test', max_length=50),
            preserve_default=False,
        ),
    ]
