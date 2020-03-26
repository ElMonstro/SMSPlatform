from itertools import chain

from django.shortcuts import get_object_or_404
from django.db.utils import IntegrityError
from django.core.mail import send_mail
from django.conf import settings

from rest_framework.exceptions import ValidationError
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from . import models
from core.utils.sms_helpers import (send_sms, 
create_personalized_message, send_mass_unique_sms, count_sms,
count_personalized_sms, update_sms_count, update_email_count)
from core.utils.helpers import (soft_delete_owned_object, 
CsvExcelReader, add_country_code, raise_validation_error)
from core.utils.validators import (validate_primary_keys, 
validate_phone_list, validate_excel_csv, validate_csv_row,
validate_first_name_column, get_intnl_phone)


class SMSRequestSerializer(serializers.ModelSerializer):

    recepients = serializers.ListField(
        required=False, validators=[validate_phone_list], child=serializers.CharField()
    )
    groups = serializers.ListField(child=serializers.PrimaryKeyRelatedField(queryset=models.SMSGroup.objects.all()), write_only=True)

    def get_fields(self, *args, **kwargs):
        fields = super().get_fields(*args, **kwargs)  
        company = self.context["request"].user.company
        medium = self.context["request"].query_params.get("medium")
        model_mapping = {
            None: models.SMSGroup,
            'email': models.EmailGroup
        }
        fields["groups"].child.queryset = model_mapping[medium].objects.filter(company=company)
        return fields


    def is_valid(self, raise_exception):
        recepients = self.initial_data.get("recepients")
        groups = self.initial_data.get("groups")
        if not recepients and not groups:
            raise ValidationError(
               {"detail": "A receipient group id or a recepient phone number list must be provided"}
            )
        return super().is_valid(raise_exception)

    def create(self, validated_data):
        recepients = self.get_receipients(validated_data)
        validated_data["recepients"] = recepients
        company = self.context["request"].user.company
        sms_count = count_sms(validated_data["message"], recepients)
        update_sms_count(sms_count, company)
        send_sms(validated_data["message"], recepients)
        validated_data["sms_count"] = sms_count
        return self.save_request(validated_data, super().create)

    def save_request(self, validated_data, save):
        groups = validated_data.pop("groups", [])
        instance = save(self, validated_data)
        instance.groups.add(*groups)
        instance.save()
        return instance

    def get_receipients(self, validated_data):
        recepients = validated_data.get("recepients", [])
        groups = validated_data.get("groups")
    
        if groups:
            merged_queryset = models.GroupMember.objects.none()
            for group in groups:
                merged_queryset = merged_queryset | group.members.all()
            if not merged_queryset:
                raise ValidationError(
                {"detail": "There are no members in the specified group(s)"}
                )
            medium = self.context["request"].query_params.get("medium", "phone")

            group_recepients = list(merged_queryset.values_list(medium, flat=True))
            recepients = set(recepients + group_recepients)
        
        return list(recepients)

    class Meta:
        model = models.SMSRequest
        fields = ["message", "groups", "recepients"]
        extra_kwargs = {'company': {'read_only':True}}

class EmailRequestSerializer(SMSRequestSerializer):

    def create(self, validated_data):
        recepients = self.get_receipients(validated_data)
        validated_data["recepients"] = recepients
        subject = validated_data["subject"]
        message = validated_data["message"]
        company = self.context["request"].user.company
        email_count = len(recepients)
        validated_data["email_count"] = email_count
        from_email = settings.COMPANY_EMAIL
        send_mail(subject, message, from_email, recepients)
        return self.save_request(validated_data, serializers.ModelSerializer.create)
        
    class Meta:
        model = models.EmailRequest
        fields = ["message", "subject", "groups", "recepients"]
        extra_kwargs = {'company': {'read_only':True}}

class SMSGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SMSGroup
        fields = "__all__"
        extra_kwargs = {'company': {'read_only':True}}


class EmailGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EmailGroup
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
        if self.context["request"].user.is_anonymous:
            return fields
        company = self.context["request"].user.company
        fields["group"].queryset = self.Meta.group_model.objects.filter(company=company)
        return fields

    def save(self, **kwargs):
        group = self.validated_data.pop("group")
        instance = super().save(**kwargs)
        group.members.add(instance)
        return instance
    class Meta:
        model = models.GroupMember
        group_model = models.SMSGroup
        fields = "__all__"
        extra_kwargs = {'company': {'read_only':True}}


class EmailGroupMemberSerializer(GroupMemberSerializer):
    
    class Meta:
        model = models.EmailGroupMember
        group_model = models.EmailGroup
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


class EmailGroupMemberUploadSerializer(serializers.Serializer):
    email = serializers.EmailField()
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)


headers_mapping = {
        None: ['phone'],
        'email': ['email']
    }

serializer_model_mapping = {
        None: (GroupMemberUploadSerializer, models.GroupMember),
        "email": (EmailGroupMemberUploadSerializer, models.EmailGroupMember)
    }

class CsvMembersUploadSerializer(serializers.Serializer):
    file = serializers.FileField(validators=[validate_excel_csv], required=True)
    group = serializers.PrimaryKeyRelatedField(queryset=models.SMSGroup.objects.all())

    def get_fields(self, *args, **kwargs):
        fields = super().get_fields(*args, **kwargs)  
        company = self.context["request"].user.company
        medium = self.context["request"].query_params.get("medium")
        model_mapping = {
            None: models.SMSGroup,
            'email': models.EmailGroup
        }
        fields["group"].queryset = model_mapping[medium].objects.filter(company=company)
        return fields
    
    def save(self, *args, **kwargs):
        """Saves all valid data to the database while adding them to group if passed"""
        file = self.validated_data["file"]
        medium = self.context["request"].query_params.get("medium")
        serializer_class, model = serializer_model_mapping[medium]
        required_headers = headers_mapping[medium]
        csv_excel_reader = CsvExcelReader(file, required_headers)
        members = []
        skipped_lines = []
        group = self.validated_data["group"]

        for i, row in csv_excel_reader.data.iterrows():
            serializer = serializer_class(data=dict(row))
            is_valid = serializer.is_valid()
            if not is_valid:
                skipped_lines.append(i+1)
                continue
            if not medium:
                intnl_phone = get_intnl_phone(serializer)
                if not intnl_phone:
                    skipped_lines.append(i+1)
                    continue
                serializer.validated_data["phone"] = intnl_phone

            serializer.validated_data["company"] = group.company
            try:
                instance, _ = model.objects.get_or_create(**serializer.validated_data)
            except IntegrityError: # catch unique together error
                skipped_lines.append(i+1)
                continue
            members.append(instance)
            group.members.add(instance)
        group.save()
        members = serializer_class(members, many=True).data
        data = {"members": members}
        if skipped_lines:
            data["skipped_lines"] = f"The following lines were skipped: {str(skipped_lines)[1:-1]} because of invalid or duplicate {required_headers[0]}s"
        return data


class PersonalizedMsgSerializer(serializers.Serializer):
    phone = serializers.CharField()
    first_name = serializers.CharField(validators=[validate_first_name_column])
    last_name = serializers.CharField(required=False)



validation_mapping = {
            "sms": (GroupMemberUploadSerializer, ["phone"]),
            "personalized": (PersonalizedMsgSerializer, ["phone", "first_name"]),
            "email": (EmailGroupMemberSerializer, ["email", "subject"])
        }

class CsvSmsContactUpload(serializers.Serializer):
    file = serializers.FileField(validators=[validate_excel_csv])
    message = serializers.CharField(required=True)
    greeting_text = serializers.CharField(required=False)
    subject = serializers.CharField(required=False)
    
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
        recepients, skipped_lines = self.read_csv(validate="personalized")
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

    def send_email(self):
        file = self.validated_data["file"]
        message = self.validated_data["message"]
        subject = self.validated_data.get("subject")
        if not subject:
            raise raise_validation_error({"subject": "This field is required."})
        required_headers = ["email"]
        csv_excel_reader = CsvExcelReader(file, required_headers)
        recepients = []
        skipped_lines = []

        for i, row in csv_excel_reader.data.iterrows():
            serializer = EmailGroupMemberUploadSerializer(data=dict(row))
            is_valid = serializer.is_valid()
            if not is_valid:
                skipped_lines.append(i+1)
                continue

            email = serializer.validated_data["email"]
            recepients.append(email)

        company = self.context["request"].user.company
        email_count = len(recepients)
        update_email_count(email_count, company)
        models.EmailRequest(company=company, message=message, recepients=recepients, email_count=email_count, subject=subject)
        from_email = settings.COMPANY_EMAIL
        send_mail(subject, message, from_email, recepients)
        data = {"recepients": recepients}
        if skipped_lines:
            data["skipped_lines"] = f"The following lines were skipped: {str(skipped_lines)[1:-1]} because of invalid or duplicate {required_headers[0]}s"
        return data

    def read_csv(self, validate="sms"):
        """
        Args: 
                personalized(bool) - used to alternate between a list of objects for
                personalized messages or a list of phone no.s for same messages
        returns: a tuple skipped lines and list of phone no.s or objects
        """
        recepients = []
        skipped_lines = []
        file = self.validated_data["file"]
        serializer_class, required_headers = validation_mapping[validate]

        csv_excel_reader = CsvExcelReader(file, required_headers)
        rows = csv_excel_reader.data.iterrows()
        for i, row in rows:
            serializer = serializer_class(data=dict(row))
            is_valid = serializer.is_valid()
            if not is_valid:
                skipped_lines.append(i+1)
                continue
            intnl_phone = get_intnl_phone(serializer)
            if not intnl_phone:
                skipped_lines.append(i+1)
                continue
            if validate == "personalized":
                first_name = serializer.validated_data["first_name"]
                contact = {"first_name": first_name, "phone": intnl_phone}
            else:
                contact = intnl_phone
                
            recepients.append(contact)
        return (recepients, skipped_lines)
