from django.db import models
from django.contrib.postgres.fields import ArrayField
from core.models import AbstractBaseModel, ActiveObjectsQuerySet
from core.utils.validators import validate_phone_list, validate_phone_number


class SMSRequest(AbstractBaseModel):
    owner = models.ForeignKey(
        "authentication.User", related_name="sms_requests", on_delete=models.CASCADE
    )
    message = models.CharField(max_length=160)
    group = models.ForeignKey(
        "SMSGroup",
        related_name="sms_requests",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    recepients = ArrayField(
        base_field=models.CharField(max_length=20), size=5, blank=True, null=True
    )

    active_objects = ActiveObjectsQuerySet.as_manager()


class SMSGroup(models.Model):
    owner = models.ForeignKey(
        "authentication.User", related_name="groups", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=60, unique=True)
    description = models.CharField(max_length=200, null=True)
    members = models.ManyToManyField("GroupMember", related_name="groups", blank=True)


class SMSTemplate(models.Model):
    owner = models.ForeignKey(
        "authentication.User", related_name="templates", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=20, null=True)
    message = models.CharField(max_length=160)

class GroupMember(AbstractBaseModel):
    owner = models.ForeignKey(
        "authentication.User", related_name="group_members", on_delete=models.CASCADE
    )
    first_name = models.CharField(max_length=30, null=True)
    last_name = models.CharField(max_length=30, null=True)
    phone = models.CharField(max_length=30, validators=[validate_phone_number], unique=True)

    active_objects = ActiveObjectsQuerySet.as_manager()
