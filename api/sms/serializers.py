from rest_framework.exceptions import ValidationError
from rest_framework import serializers
from . import models
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
        if recepients and group:
            raise ValidationError(
               {"detail": "Either send group id or receipient list not both"}
            )
        return super().is_valid(raise_exception)

    def create(self, validated_data):
        receipients = validated_data.get("recepients")
        group = validated_data.get("group")

        if group and not group.members.all():
            raise ValidationError(
               {"detail": "There are no members in the specified group"}
            )

        if group:
            receipients = group.members.all().values_list("phone", flat=True)
            receipients = list(receipients)
        else:
            validated_data["recepients"] = receipients = list(set(receipients))
        send_sms(validated_data["message"], receipients)
        return super().create(validated_data)

    class Meta:
        model = models.SMSRequest
        fields = "__all__"
        extra_kwargs = {'owner': {'read_only':True}}


class SMSGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SMSGroup
        fields = "__all__"
        extra_kwargs = {'owner': {'read_only':True}}


class SMSTemplateSerializer(serializers.ModelSerializer):

    def is_valid(self, raise_exception):
        return super().is_valid(raise_exception)

    class Meta:
        model = models.SMSTemplate
        fields = "__all__"
        extra_kwargs = {'owner': {'read_only':True}}


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
                soft_delete_owned_object(models.SMSRequest, user, pk)

class GroupMemberSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.GroupMember
        fields = "__all__"
        extra_kwargs = {'owner': {'read_only':True}}


class SingleSMSGroupSerializer(serializers.ModelSerializer):
    member_list = GroupMemberSerializer(many=True,source="members", read_only=True)
    class Meta:
        model = models.SMSGroup
        fields = "__all__"
        extra_kwargs = {'owner': {'read_only':True},
        "members": {"write_only": True}}
