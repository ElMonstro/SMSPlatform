# Generated by Django 3.0.2 on 2020-03-18 23:43

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0008_auto_20200312_1532'),
        ('sms', '0011_auto_20200225_1250'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=60)),
                ('description', models.CharField(max_length=200, null=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='company_email_groups', to='authentication.Company')),
            ],
        ),
        migrations.CreateModel(
            name='EmailRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('message', models.CharField(max_length=800)),
                ('recepients', django.contrib.postgres.fields.ArrayField(base_field=models.EmailField(max_length=254), blank=True, null=True, size=5)),
                ('sms_count', models.IntegerField(default=0)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='email_requests', to='authentication.Company')),
                ('group', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='email_requests', to='sms.EmailGroup')),
            ],
            options={
                'abstract': False,
            },
            managers=[
                ('active_objects', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='EmailGroupMember',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('first_name', models.CharField(max_length=30, null=True)),
                ('last_name', models.CharField(max_length=30, null=True)),
                ('email', models.EmailField(max_length=254)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='company_email_group_members', to='authentication.Company')),
            ],
            options={
                'unique_together': {('company', 'email')},
            },
            managers=[
                ('active_objects', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AddField(
            model_name='emailgroup',
            name='members',
            field=models.ManyToManyField(blank=True, related_name='email_groups', to='sms.EmailGroupMember'),
        ),
        migrations.AlterUniqueTogether(
            name='emailgroup',
            unique_together={('company', 'name')},
        ),
    ]