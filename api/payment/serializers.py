from datetime import datetime, timedelta

from rest_framework import serializers
from core.utils.validators import validate_mpesa_phone_number
from core.utils.mpesa_helpers import send_LNM_request, validate_mpesa_callback_request
from core.utils.helpers import camel_to_snake
from core.utils.sms_helpers import calculate_recharge_sms, update_sms_count
from . import models


class RechargeSerializer(serializers.Serializer):
    customer_number = serializers.CharField(validators=[validate_mpesa_phone_number])
    transaction_desc = serializers.CharField()
    amount = serializers.IntegerField()

    def send_request(self):
        data = self.validated_data
        data["company"] = self.context["request"].user.company
        data["amount"] = str(data["amount"])
        send_LNM_request.delay(**data)

class PaymentSerializer(serializers.ModelSerializer):

    def is_valid(self, raise_exception=False):
        data = self.initial_data["Body"]["stkCallback"]
        result_code = data.pop("ResultCode")
        initial_data = {}
        initial_data["result_code"] = result_code
        initial_data["result_desc"] = data["ResultDesc"]

        if not result_code:
            callback_meta_data_list = data["CallbackMetadata"]["Item"]
            callback_meta_data_list.remove({"Name": "Balance"})
            callback_meta_data = {camel_to_snake(item["Name"]): item["Value"] for item in callback_meta_data_list}
            # convert date to UTC
            transaction_date = datetime.strptime(str(callback_meta_data["transaction_date"]), "%Y%m%d%H%M%S") - timedelta(hours=3)
            callback_meta_data["transaction_date"] = transaction_date.strftime("%Y-%m-%dT%H:%M:%S")
            initial_data.update(callback_meta_data)
            phone_number = initial_data["phone_number"]
            recharge_request_object = models.RechargeRequest.objects.filter(customer_number=phone_number, completed=False).order_by('-id')[0]
            recharge_request_object.completed = True
            recharge_request_object.save()
            initial_data["company"] = recharge_request_object.company.id
            amount = initial_data["amount"]

            validate_mpesa_callback_request(transaction_date, recharge_request_object.created_at)
            sms_amount = calculate_recharge_sms(models.RechargePlan.objects.all(), amount)
            update_sms_count(sms_amount, recharge_request_object.company, add=True)


        self.initial_data = initial_data
        super().is_valid(raise_exception=raise_exception)

    class Meta:
        model = models.Payment
        fields = '__all__'

class RechargePlanSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.RechargePlan
        fields = '__all__'
        