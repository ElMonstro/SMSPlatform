from django.db import models
from django.contrib.postgres.fields import ArrayField
from core.models import AbstractBaseModel, ActiveObjectsQuerySet
from core.utils.validators import validate_phone_list, validate_phone_number


class SMSRequest(AbstractBaseModel):
    company = models.ForeignKey(
        "authentication.Company", on_delete=models.CASCADE,related_name="sms_requests"
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
    company = models.ForeignKey(
        "authentication.Company", on_delete=models.CASCADE,related_name="company_groups"
    )
    name = models.CharField(max_length=60)
    description = models.CharField(max_length=200, null=True)
    members = models.ManyToManyField("GroupMember", related_name="groups", blank=True)

    class Meta:
        unique_together = ('company', 'name',)


class SMSTemplate(models.Model):
    company = models.ForeignKey(
        "authentication.Company", on_delete=models.CASCADE,related_name="company_templates"
    )
    name = models.CharField(max_length=20, null=True)
    message = models.CharField(max_length=160)

class GroupMember(AbstractBaseModel):
    company = models.ForeignKey(
        "authentication.Company", on_delete=models.CASCADE,related_name="company_group_members"
    )
    first_name = models.CharField(max_length=30, null=True)
    last_name = models.CharField(max_length=30, null=True)
    phone = models.CharField(max_length=30, validators=[validate_phone_number])

    active_objects = ActiveObjectsQuerySet.as_manager()
    objects = models.Manager()

    class Meta:
        unique_together = ('company', 'phone',)
