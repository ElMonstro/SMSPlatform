from django.shortcuts import get_object_or_404
from django.db.utils import IntegrityError

from rest_framework.exceptions import ValidationError
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from . import models
from core.utils.sms_helpers import (send_sms, 
create_personalized_message, send_mass_unique_sms, count_sms,
count_personalized_sms, update_sms_count)
from core.utils.helpers import (soft_delete_owned_object, 
CsvExcelReader, add_country_code)
from core.utils.validators import (validate_primary_keys, 
validate_phone_list, validate_excel_csv, validate_csv_row,
validate_first_name_column)


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

        company = self.context["request"].user.company
        sms_count = count_sms(validated_data["message"], receipients)
        update_sms_count(sms_count, company)
        send_sms(validated_data["message"], receipients)
        validated_data["sms_count"] = sms_count
        return super().create(validated_data)

    class Meta:
        model = models.SMSRequest
        fields = "__all__"
        extra_kwargs = {'company': {'read_only':True}}


class SMSGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SMSGroup
        fields = "__all__"
        extra_kwargs = {'company': {'read_only':True}}


class SMSTemplateSerializer(serializers.ModelSerializer):

    def is_valid(self, raise_exception):
        return super().is_valid(raise_exception)

    class Meta:
        model = models.SMSTemplate
        fields = "__all__"
        extra_kwargs = {'company': {'read_only':True}}


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
    group = serializers.PrimaryKeyRelatedField(queryset=models.SMSGroup.objects.all(), write_only=True)

    def get_fields(self, *args, **kwargs):
        fields = super().get_fields(*args, **kwargs)  
        company = self.context["request"].user.company
        fields["group"].queryset = models.SMSGroup.objects.filter(company=company)
        return fields

    def save(self, **kwargs):
        group = self.validated_data.pop("group")
        instance = super().save(**kwargs)
        group.members.add(instance)
        return instance
    class Meta:
        model = models.GroupMember
        fields = "__all__"
        extra_kwargs = {'company': {'read_only':True}}


class SingleSMSGroupSerializer(serializers.ModelSerializer):
    member_list = GroupMemberSerializer(many=True,source="members", read_only=True)
    class Meta:
        model = models.SMSGroup
        fields = "__all__"
        extra_kwargs = {'company': {'read_only':True},
        "members": {"write_only": True}}

class GroupMemberUploadSerializer(serializers.Serializer):
    phone = serializers.CharField()
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)

class CsvMembersUploadSerializer(serializers.Serializer):
    file = serializers.FileField(validators=[validate_excel_csv], required=True)
    group = serializers.PrimaryKeyRelatedField(queryset=models.SMSGroup.objects.all())
    
    def save(self, *args, **kwargs):
        """Saves all valid data to the database while adding them to group if passed"""
        file = self.validated_data["file"]
        required_headers = ["phone"]
        csv_excel_reader = CsvExcelReader(file, required_headers)
        members = []
        skipped_lines = []
        group = self.validated_data["group"]
        for i, row in csv_excel_reader.data.iterrows():
            serializer = GroupMemberUploadSerializer(data=dict(row))
            intnl_phone = validate_csv_row(serializer)
            if not intnl_phone:
                skipped_lines.append(i+1)
            serializer.validated_data["phone"] = intnl_phone
            serializer.validated_data["company"] = group.company
            try:
                instance, _ = models.GroupMember.objects.get_or_create(**serializer.validated_data)

            except IntegrityError: # catch unique together error
                skipped_lines.append(i+1)
                continue
            members.append(instance)
            group.members.add(instance)
        group.save()
        members = GroupMemberUploadSerializer(members, many=True).data
        data = {"members": members}
        if skipped_lines:
            data["skipped_lines"] = f"The following lines were skipped: {str(skipped_lines)[1:-1]} because of invalid or duplicate phone numbers"
        return data


class PersonalizedMsgSerializer(serializers.Serializer):
    phone = serializers.CharField()
    first_name = serializers.CharField(validators=[validate_first_name_column])
    last_name = serializers.CharField(required=False)


class CsvSmsContactUpload(serializers.Serializer):
    file = serializers.FileField(validators=[validate_excel_csv])
    message = serializers.CharField(required=True)
    greeting_text = serializers.CharField(required=False)
    
    def send_sms(self):
        """Send sms to csv uploaded contacts"""
        message = self.validated_data["message"]
        recepients, skipped_lines = self.read_csv()
        company = self.context["request"].user.company
        recepients = list(set(recepients))
        sms_count = count_sms(message, recepients)
        update_sms_count(sms_count, company)
        send_sms.delay(message, recepients)
        sms_request = models.SMSRequest(message=message, recepients=recepients, company=company, sms_count=sms_count)
        sms_request.save()
        data = {
            "recepients": recepients,
            "sms_count": sms_count
            }
        if skipped_lines:
            data["skipped_lines"] = f"The following lines were skipped: {str(skipped_lines)[1:-1]}, because of invalid phone numbers"

        return data


    def send_personalized_sms(self):
        """Deals with sending personalized messages to csv contacts"""
        greeting_text = self.validated_data.get("greeting_text")

        if not greeting_text:
            raise ValidationError({"greeting_text": "There must be a greeting message for personalized messages"})
        recepients, skipped_lines = self.read_csv(personalized=True)
        message = self.validated_data["message"]
        company = self.context["request"].user.company
        sms_count = count_personalized_sms(message, greeting_text, recepients)
        update_sms_count(sms_count, company)
        sms_request = models.SMSRequest(message=message, recepients=[contact["phone"] for contact in recepients], company=company, sms_count=sms_count)
        sms_request.save()
        send_mass_unique_sms.delay(message, greeting_text, recepients)
        data = {
            "recepients": recepients,
            "sms_count": sms_count
            }
        if skipped_lines:
            data["skipped_lines"] = f"The following lines were skipped: {str(skipped_lines)[1:-1]}" \
            + ", because of invalid phone numbers or don't have first names "

        return data


    def read_csv(self, personalized=False):
        """
        Args: 
                personalized(bool) - used to alternate between a list of objects for
                personalized messages or a list of phone no.s for same messages
        returns: a tuple skipped lines and list of phone no.s or objects
        """
        recepients = []
        skipped_lines = []
        file = self.validated_data["file"]
        if personalized:
            required_headers = ["phone", "first_name"]
            serializer_class = PersonalizedMsgSerializer
        else:
            required_headers = ["phone"]
            serializer_class = GroupMemberUploadSerializer

        csv_excel_reader = CsvExcelReader(file, required_headers)
        for i, row in csv_excel_reader.data.iterrows():
            serializer = serializer_class(data=dict(row))
            intnl_phone = validate_csv_row(serializer)
            if not intnl_phone:
                skipped_lines.append(i+1)
                continue
            if personalized:
                first_name = serializer.validated_data["first_name"]
                contact = {"first_name": first_name, "phone": intnl_phone}
            else:
                contact = intnl_phone

            recepients.append(contact)
        return (recepients, skipped_lines)
