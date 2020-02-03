from rest_framework.exceptions import ValidationError
from rest_framework import serializers
from .models import SMSGroup, SMSRequest, SMSTemplate
from core.utils.sms_helpers import send_sms
from core.utils.validators import validate_phone_list
from core.utils.helpers import soft_delete_owned_object
from core.utils.validators import validate_primary_keys


class SMSRequestSerializer(serializers.ModelSerializer):

    recepients = serializers.ListField(
        required=False, validators=[validate_phone_list], child=serializers.CharField()
    )

    def is_valid(self, raise_exception):
        recepients = self.initial_data.get("recepients")
        group = self.initial_data.get("group")
        if not recepients and not group:
            raise ValidationError(
               {"detail": "A receipient group id or a recepient phone number list must be provided"}
            )
        return super().is_valid(raise_exception)

    def create(self, validated_data):
        receipients = validated_data["recepients"]
        send_sms(validated_data["message"], receipients)
        return super().create(validated_data)

    class Meta:
        model = SMSRequest
        fields = "__all__"
        extra_kwargs = {'owner': {'read_only':True}}


class SMSGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = SMSGroup
        fields = "__all__"


class SMSTemplateSerializer(serializers.ModelSerializer):
    def is_valid(self, raise_exception):
        self.initial_data["owner"] = self.context["request"].user.pk
        return super().is_valid(raise_exception)

    class Meta:
        model = SMSTemplate
        fields = "__all__"


class DeleteSMSRequestsSerializer(serializers.Serializer):

    sms_requests = serializers.ListSerializer(
        child=serializers.IntegerField(required=True)
    )



    def delete(self):
        sms_requests = self.data.get("sms_requests")
        user = self.context["request"].user
        if sms_requests:
            validate_primary_keys(sms_requests)
            for pk in sms_requests:
                soft_delete_owned_object(SMSRequest, user, pk)
