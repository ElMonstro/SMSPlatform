from django.db import models
from django.contrib.postgres.fields import ArrayField
from core.models import AbstractBaseModel, ActiveObjectsQuerySet
from core.utils.validators import validate_phone_list, validate_phone_number


class SMSRequest(AbstractBaseModel):
    company = models.ForeignKey(
        "authentication.Company", on_delete=models.CASCADE,related_name="sms_requests"
    )
    message = models.CharField(max_length=800)
    groups = models.ManyToManyField("SMSGroup", related_name="sms_groups", blank=True)
    recepients = ArrayField(
        base_field=models.CharField(max_length=20), blank=True, null=True
    )
    sms_count = models.IntegerField(default=0)

    objects = ActiveObjectsQuerySet.as_manager()

class EmailRequest(AbstractBaseModel):
    company = models.ForeignKey(
        "authentication.Company", on_delete=models.CASCADE,related_name="email_requests"
    )
    message = models.CharField(max_length=800)
    groups = models.ManyToManyField("EmailGroup", related_name="email_groups", blank=True)
    recepients = ArrayField(
        base_field=models.EmailField(), blank=True, null=True
    )
    email_count = models.IntegerField(default=0)
    subject = models.CharField(max_length=800)

    objects = ActiveObjectsQuerySet.as_manager()


class SMSGroup(models.Model):
    company = models.ForeignKey(
        "authentication.Company", on_delete=models.CASCADE,related_name="company_groups"
    )
    name = models.CharField(max_length=60)
    description = models.CharField(max_length=200, null=True)
    members = models.ManyToManyField("GroupMember", related_name="groups", blank=True)

    class Meta:
        unique_together = ('company', 'name',)


class EmailGroup(models.Model):
    company = models.ForeignKey(
        "authentication.Company", on_delete=models.CASCADE,related_name="company_email_groups"
    )
    name = models.CharField(max_length=60)
    description = models.CharField(max_length=200, null=True)
    members = models.ManyToManyField("EmailGroupMember", related_name="email_groups", blank=True)

    class Meta:
        unique_together = ('company', 'name',)


class SMSTemplate(models.Model):
    company = models.ForeignKey(
        "authentication.Company", on_delete=models.CASCADE,related_name="company_templates"
    )
    name = models.CharField(max_length=20, null=True)
    message = models.CharField(max_length=800)

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


class EmailGroupMember(AbstractBaseModel):
    company = models.ForeignKey(
        "authentication.Company", on_delete=models.CASCADE,related_name="company_email_group_members"
    )
    first_name = models.CharField(max_length=30, null=True)
    last_name = models.CharField(max_length=30, null=True)
    email = models.EmailField()

    active_objects = ActiveObjectsQuerySet.as_manager()
    objects = models.Manager()

    class Meta:
        unique_together = ('company', 'email',)


class SMSBranding(models.Model):
    name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    company = models.OneToOneField(
        "authentication.Company", on_delete=models.CASCADE,related_name="brand"
    )


class SentSMS(models.Model):
    company = models.ForeignKey(
        "authentication.Company", on_delete=models.CASCADE,related_name="sent_sms"
    )
    message_id = models.CharField(max_length=60, primary_key=True)
    status = models.CharField(max_length=30)
    status_code = models.IntegerField()


class DeliveredSMS(AbstractBaseModel):
    sent_sms = models.OneToOneField(
        "SentSMS", on_delete=models.CASCADE,related_name="brand"
        )
    status = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=30)
    network_code = models.CharField(max_length=10)
    network = models.CharField(max_length=30)
    failure_reason = models.CharField(max_length=30, null=True)
    retry_count = models.CharField(max_length=30, null=True)
