import json

from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework.exceptions import ValidationError
from rest_framework import serializers
from django_celery_beat.models import CrontabSchedule, PeriodicTask

from api.sms.models import SMSGroup
from .models import ScheduleRegistry

class CrontabScehduleSerializer(serializers.ModelSerializer):

    group = serializers.PrimaryKeyRelatedField(queryset=SMSGroup.objects.all())
    message = serializers.CharField()
    name = serializers.CharField()
    expires = serializers.DateTimeField(required=False)
    one_off = serializers.BooleanField(required=False)

    def get_fields(self, *args, **kwargs):
        fields = super().get_fields(*args, **kwargs)  
        company = self.context["request"].user.company
        fields["group"].queryset = SMSGroup.objects.filter(company=company)
        return fields


    def save(self, **kwargs):
        group = self.validated_data.pop("group")
        receipients = group.members.all().values_list("phone", flat=True)
        receipients = list(receipients)
        message = self.validated_data.pop("message")
        name = self.validated_data.pop("name")
        expires = self.validated_data.pop("expires", None)
        one_off = self.validated_data.pop("expires", False)
        hour = self.validated_data.pop("expires", False)
        if hour:
            # convert to UTC
            self.validated_data["hour"] = hour - 3
        crontab_schedule_instance, _ = CrontabSchedule.objects.get_or_create(**self.validated_data)
        company = self.context["request"].user.company
        name = company.name + '-' + name
        try:
            periodic_task_instance = PeriodicTask.objects.create(
                crontab=crontab_schedule_instance,
                name=name,
                task="send_sms",
                args=json.dumps([message, receipients]),
                expires=expires,
                one_off=one_off
            )
        except DjangoValidationError as err:
            raise ValidationError(err.message_dict)

        company_schedules_instance, _ = ScheduleRegistry.objects.get_or_create(company=company)
        company_schedules_instance.schedules.add(periodic_task_instance)
        company_schedules_instance.save()
        return periodic_task_instance


    class Meta:
        model = CrontabSchedule
        fields = ['minute', 'hour', 'day_of_week', 'day_of_month', 'month_of_year', 'group', 'message', "expires", "name", "one_off"]


class SMSScheduleSerializer(serializers.Serializer):

    group = serializers.PrimaryKeyRelatedField(queryset=SMSGroup.objects.all())
    
    def get_fields(self, *args, **kwargs):
        fields = super().get_fields(*args, **kwargs)  
        company = self.context["request"].user.company
        fields["group"].queryset = SMSGroup.objects.filter(company=company)
        return fields


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
    crontab = UpdateScheduleTimeSerializer(read_only=True)
    class Meta:
        model = PeriodicTask
        fields = '__all__'
