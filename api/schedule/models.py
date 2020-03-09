from django.db import models
from django_celery_beat.models import PeriodicTask

class ScheduleRegistry(models.Model):
    company = models.ForeignKey(
        "authentication.Company", on_delete=models.CASCADE, related_name="sms_schedules",
    )
    schedules = models.ManyToManyField(PeriodicTask, related_name="schedules")
