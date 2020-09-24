from django.db import models

from core.models import AbstractBaseModel, ActiveObjectsQuerySet

# Create your models here.
PAYMENT_ACTIONS = (
    ("brand_payment", "brand_payment"),
    ("sms_topup", "sms_topup"),
    ("email_topup", "email_topup")
)
class Payment(AbstractBaseModel):
    company = models.ForeignKey("authentication.Company", on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey("authentication.User", on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(decimal_places=2, max_digits=9)
    payment_action = models.CharField(max_length=20, choices=PAYMENT_ACTIONS, default="sms_topup")
    ref_no = models.OneToOneField("PaymentKey", on_delete=models.SET_NULL, to_field="ref_no", db_column="ref_no", null=True)

    def __str__(self):
        return f'Amount: {self.amount}'


class RechargePlan(models.Model):
    name = models.CharField(max_length=50, unique=True)
    price_limit = models.IntegerField(unique=True)
    rate = models.DecimalField(decimal_places=2, max_digits=3)

    def __str__(self):
        return str(self.price_limit)


class ResellerRechargePlan(models.Model):
    company = models.ForeignKey("authentication.Company", on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    price_limit = models.IntegerField()
    rate = models.DecimalField(decimal_places=2, max_digits=3)

    def __str__(self):
        return str(self.price_limit)
    class Meta:
        unique_together = ('company', 'price_limit')

class BrandingFee(models.Model):
    fee = models.DecimalField(decimal_places=2, max_digits=10)
    

class PaymentKey(AbstractBaseModel):
    ref_no = models.CharField(max_length=60, unique=True)
    is_active = models.BooleanField(default=True)
