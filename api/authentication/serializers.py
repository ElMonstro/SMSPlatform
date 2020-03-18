from datetime import datetime
from jwt import encode, decode, DecodeError

from django.db.utils import IntegrityError
from django.contrib.auth.password_validation import validate_password
from django.conf import settings
from django.shortcuts import get_object_or_404

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from core.utils.validators import validate_phone_number
from core.utils.helpers import get_errored_integrity_field
from .models import User, AddStaffModel, Company


class CompanySerializer(serializers.ModelSerializer):

    class Meta:
        fields = "__all__"
        model = Company


class RegistrationSerializer(serializers.Serializer):
    """
    Serializer for handling user registration
    """

    email = serializers.EmailField()
    phone = serializers.CharField(required=False, validators=[validate_phone_number])
    full_name = serializers.CharField(max_length=100)
    company = serializers.CharField(max_length=50)
    password = serializers.CharField(max_length=124, min_length=8, write_only=True)
    confirmed_password = serializers.CharField(
        max_length=124, min_length=8, write_only=True
    )
    county = serializers.CharField(max_length=50, write_only=True)
    company_data = CompanySerializer(read_only=True, source='company')

    def validate(self, data):
        """validate data before it gets saved"""
        confirmed_password = data.get("confirmed_password")

        try:
            validate_password(data["password"])
        except ValidationError as e:
            raise serializers.ValidationError({"password": e.messages}) from e

        if not self.do_passwords_match(data["password"], confirmed_password):
            raise serializers.ValidationError({"password": "passwords don't match"})

        return data

    def create(self, validated_data):
        validated_data.pop("confirmed_password")
        try:
            user = self.Meta.create_user(**validated_data)
            return user
        except IntegrityError as exc:
            errored_field = get_errored_integrity_field(exc)
            if errored_field:
                raise serializers.ValidationError(
                    {
                        errored_field: f"A user is already registered with this {errored_field}."
                    }
                ) from exc
        except ValidationError as exc:
            raise serializers.ValidationError(exc.args[0]) from exc

    @staticmethod
    def do_passwords_match(password1, password2):

        return password1 == password2

    class Meta:
        create_user = User.objects.create_user

class AddStaffSerializer(serializers.ModelSerializer):
    
    def save(self):
        company_name = self.context["request"].user.company.name
        payload = { 
            "email": self.validated_data["email"],
            "company": company_name,
            "date": datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
             }
        token = encode(payload, settings.SECRET_KEY)
        self.validated_data["token"] = token
        return super().save()
    class Meta:
        model = AddStaffModel
        fields = ["email"]
        extra_kwargs = {'token': {'read_only':True}}


class StaffRegistrationSerializer(RegistrationSerializer):

    token = serializers.CharField(required=True, write_only=True)
    company = CompanySerializer(read_only=True)
    email = serializers.ReadOnlyField()

    def get_fields(self, *args, **kwargs):
        fields = super().get_fields(*args, **kwargs)  
        fields.pop("county")
        return fields

    def is_valid(self, **kwargs):
        super().is_valid(**kwargs)
        token = self.validated_data["token"]
        try:
            payload = decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        except DecodeError:
            raise ValidationError({"detail": "Invalid token"})
        payload.pop("date")
        self.validated_data.pop("token")
        self.validated_data.update(payload)

    class Meta:
        create_user = User.objects.create_staff


class ResellerRegistration(RegistrationSerializer):

    class Meta:
        create_user = User.objects.create_reseller


class ResellerClientSerializer(RegistrationSerializer):

    def validate(self, data):
        super().validate(data)
        company_name = self.context['request'].query_params.get("parent_company")
        company = get_object_or_404(Company, name=company_name)
        if not company.is_reseller:
            raise ValidationError({"detail": "Company specified in query params is not a reseller"})
        data.update({"parent_company": company})
        return data

    class Meta:
        create_user = User.objects.create_reseller_client
