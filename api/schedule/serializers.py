import json

from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework.exceptions import ValidationError
from rest_framework import serializers
from django_celery_beat.models import CrontabSchedule, PeriodicTask

from api.sms.models import SMSGroup, EmailGroup
from .models import ScheduleRegistry


class CrontabScehduleSerializer(serializers.ModelSerializer):

    group = serializers.PrimaryKeyRelatedField(queryset=SMSGroup.objects.all())
    message = serializers.CharField()
    subject = serializers.CharField(required=False)
    name = serializers.CharField()
    expires = serializers.DateTimeField(required=False)
    one_off = serializers.BooleanField(required=False)

    def get_fields(self, *args, **kwargs):
        fields = super().get_fields(*args, **kwargs)  
        company = self.context["request"].user.company
        
        if self.context["request"].query_params.get("medium") == "email":
            fields["subject"].required = True
            fields["group"].queryset = EmailGroup.objects.filter(company=company)
        else:
            fields["group"].queryset = SMSGroup.objects.filter(company=company)
        return fields

    def save(self, **kwargs):
        group = self.validated_data.pop("group")
        message = self.validated_data.pop("message")
        name = self.validated_data.pop("name")
        expires = self.validated_data.pop("expires", None)
        one_off = self.validated_data.pop("one_off", False)
        company = self.context["request"].user.company

        hour = self.validated_data.pop("hour", None)
        if hour:
            # convert to UTC
            self.validated_data["hour"] = str(int(hour) - 3)

        medium = self.context["request"].query_params.get("medium", "phone")
        receipients = group.members.all().values_list(medium, flat=True)
        receipients = list(receipients)
    
        if medium == "email":     
            subject = self.validated_data.pop("subject", None)
            task = "djcelery_email_send_multiple"
            args = json.dumps([subject, message, company.name, receipients])
        else:
            args = json.dumps([message, receipients, company.pk])
            task = "send_sms"
        
        crontab_schedule_instance, _ = CrontabSchedule.objects.get_or_create(**self.validated_data)
        name = company.name + '-' + name

        try:
            periodic_task_instance = PeriodicTask.objects.create(
                crontab=crontab_schedule_instance,
                name=name,
                task=task,
                args=args,
                expires=expires,
                one_off=one_off
            )
        except DjangoValidationError as err:
            raise ValidationError(err.error_dict)

        company_schedules_instance, _ = ScheduleRegistry.objects.get_or_create(company=company)
        company_schedules_instance.schedules.add(periodic_task_instance)
        company_schedules_instance.save()
        return periodic_task_instance


    class Meta:
        model = CrontabSchedule
        fields = ['minute', 'hour', 'day_of_week', 'day_of_month', 'month_of_year', 'group', 'message', "expires", "name", "one_off", "subject"]


class UpdateScheduleTimeSerializer(serializers.ModelSerializer):   

    def update(self, instance, validated_data):
        crontab, _ = CrontabSchedule.objects.get_or_create(**validated_data)
        instance.crontab = crontab
        instance.save()
        return instance

    class Meta:
        model = CrontabSchedule
        fields = ['minute', 'hour', 'day_of_week', 'day_of_month', 'month_of_year']


class PeriodicTaskSerializer(serializers.ModelSerializer):

    group = serializers.PrimaryKeyRelatedField(queryset=SMSGroup.objects.all(), write_only=True)
    message = serializers.CharField(write_only=True)
    subject = serializers.CharField(required=False, write_only=True)
    crontab = UpdateScheduleTimeSerializer(read_only=True)

    def get_fields(self, *args, **kwargs):
        fields = super().get_fields(*args, **kwargs)
        
        if self.context["request"].user.is_anonymous:
            return fields 
        company = self.context["request"].user.company
        
        if self.context["request"].query_params.get("medium") == "email":
            fields["subject"].required = True
            fields["group"].queryset = EmailGroup.objects.filter(company=company)
        else:
            fields["group"].queryset = SMSGroup.objects.filter(company=company)
        return fields

    def update(self, instance, validated_data):
        group = validated_data.pop("group", None)
        medium = self.context["request"].query_params.get("medium", "phone")

        receipients = None

        if group:
            receipients = group.members.all().values_list(medium, flat=True)
            receipients = list(receipients)
    
        if medium == "email":
            subject = validated_data.pop("subject", instance.args[0]) 
            message = validated_data.pop("message", instance.args[1])
            receipients = receipients or instance.args[3]
            args = json.dumps([subject, message, instance.args[2], receipients])
            instance.args = args
        else:
            message = validated_data.pop("message", instance.args[0])
            receipients = receipients or instance.args[1]
            args = json.dumps([message, receipients])
            instance.args = args

        return super().update(instance, validated_data)
    class Meta:
        model = PeriodicTask
        fields = '__all__'
