from django.db import models

from core.models import AbstractBaseModel, ActiveObjectsQuerySet

# Create your models here.
class Payment(AbstractBaseModel):
    company = models.ForeignKey("authentication.Company", on_delete=models.SET_NULL, null=True)
    result_code = models.IntegerField()
    result_desc = models.CharField(max_length=100)
    amount = models.IntegerField(null=True)
    mpesa_receipt_number = models.CharField(max_length=20, null=True, unique=True)
    transaction_date = models.DateTimeField(null=True)
    phone_number = models.CharField(max_length=20, null=True)

    def __str__(self):
        return self.mpesa_receipt_number


class RechargePlan(models.Model):
    company = models.ForeignKey("authentication.Company", on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=50)
    price_limit = models.IntegerField()
    rate = models.DecimalField(decimal_places=2, max_digits=3)

    def __str__(self):
        return str(self.price_limit)


class RechargeRequest(AbstractBaseModel):
    company = models.ForeignKey("authentication.Company", on_delete=models.SET_NULL, null=True)
    customer_number = models.CharField(max_length=20)
    checkout_request_id = models.CharField(max_length=50)
    response_code = models.CharField(max_length=20)
    completed  = models.BooleanField(default=False)

    def __str__(self):
        return self.checkout_request_id
