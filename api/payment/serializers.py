from datetime import datetime, timedelta

from rest_framework import serializers
from core.utils.validators import (validate_mpesa_phone_number, transaction_description_validator,
 validate_if_branding_fee_is_set, validate_branding_fee)
from core.utils.mpesa_helpers import send_LNM_request, validate_mpesa_callback_request
from core.utils.helpers import camel_to_snake, raise_validation_error
from core.utils.sms_helpers import calculate_recharge_sms, update_sms_count, send_sms, company_is_branded
from core.utils.encryption_helpers import decrypt_string
from . import models



class MpesaPaySerializer(serializers.Serializer):
    customer_number = serializers.CharField(validators=[validate_mpesa_phone_number])
    transaction_desc = serializers.CharField(validators=[transaction_description_validator])
    amount = serializers.IntegerField()

    
    def is_valid(self, raise_exception=False):
        is_valid = super().is_valid(raise_exception=raise_exception)
        if self.validated_data["transaction_desc"] == "brand_payment":
            fee_queryset = models.BrandingFee.objects.all()
            validate_if_branding_fee_is_set(fee_queryset)
            validate_branding_fee(fee_queryset[0].fee, self.validated_data["amount"])
            company = self.context["request"].user.company
            if not company_is_branded(company):
                raise_validation_error({"detail": "Please request for branding before you pay for it"})
        return is_valid


    def send_request(self):
        data = self.validated_data
        data["company"] = self.context["request"].user.company
        data["amount"] = str(data["amount"])
        send_LNM_request.delay(**data)

class PaymentSerializer(serializers.ModelSerializer):

    def is_valid(self, raise_exception=False):
        user = self.context["request"].user
        super().is_valid(raise_exception=True)
        self.validated_data["user"] = user
        payment_action = self.validated_data.get("payment_action")
        if not payment_action:
            payment_action = 'sms_topup'

        encrypted_amount = self.validated_data["amount"]
        
        amount = decrypt_string(encrypted_amount)
        message = self.get_payment_action(payment_action)(amount)
        return message

    
    
    def create_recharge_rates_queryset(self):
        company = self.context["request"].user.company
        parent_company = company.parent
        if parent_company:
            queryset = models.ResellerRechargePlan.objects.filter(company=parent_company)
        else:
            queryset = models.RechargePlan.objects.all()
        return queryset

    def update_branding_status(self, amount=None):
        company = self.context["request"].user.company
        company.brand.is_active = True
        company.brand.save()
        message = f'Branding has been activated.'
        phone_number = self.context["request"].user.phone
        self.send_message(message, [phone_number])
        return message
        

    def update_sms_data(self, amount):
        company = self.context["request"].user.company
        recharge_rates_queryset = self.create_recharge_rates_queryset()
        sms_amount = calculate_recharge_sms(recharge_rates_queryset, amount)
        new_sms_balance  = update_sms_count(sms_amount, company, add=True)
        phone_number = self.context["request"].user.phone
        message = f'The recharge request was successful. Your new SMS balance is {new_sms_balance}.'
        self.send_message(message, [phone_number])
        return message

    def get_payment_action(self, transaction_desc):
        """Get appropriate action depending on transaction description"""
        action_mapping = {
            "sms_topup": self.update_sms_data,
            "brand_payment": self.update_branding_status
        }
        return action_mapping[transaction_desc]

    def send_message(self, message, contact_list):
        send_sms.delay(message, contact_list)
    class Meta:
        model = models.Payment
        fields = '__all__'

class RechargePlanSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.RechargePlan
        fields = '__all__'


class ResellerRechargePlanSeializer(serializers.ModelSerializer):
    
    class Meta:
        fields = "__all__"
        model = models.ResellerRechargePlan
        extra_kwargs = {'company': {'read_only':True}}


class BrandingFeeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = models.BrandingFee
