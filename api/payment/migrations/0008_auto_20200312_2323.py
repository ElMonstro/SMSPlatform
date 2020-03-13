# Generated by Django 3.0.2 on 2020-03-12 23:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0008_auto_20200312_1532'),
        ('payment', '0007_auto_20200312_0656'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rechargeplan',
            name='company',
        ),
        migrations.CreateModel(
            name='ResellerRechargePlan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('price_limit', models.IntegerField()),
                ('rate', models.DecimalField(decimal_places=2, max_digits=3)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='authentication.Company')),
            ],
            options={
                'unique_together': {('company', 'price_limit')},
            },
        ),
    ]