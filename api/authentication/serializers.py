from datetime import datetime, timedelta
from jwt import encode, decode, DecodeError
from faker import Faker

from django.db.utils import IntegrityError
from django.contrib.auth.password_validation import validate_password
from django.conf import settings
from django.shortcuts import get_object_or_404

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from core.utils.validators import validate_phone_number
from core.utils.helpers import get_errored_integrity_field, raise_validation_error
from .models import User, AddStaffModel, Company, ResetPasswordToken, ConsumerKey, APIKeyActivity

fake = Faker()
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
        error_dict = {}
        confirmed_password = data.get("confirmed_password")
        company = data.get("company")
        email = data.get("email")
        phone = data.get("phone")

        company = Company.objects.filter(name=company)

        if company:
            error_dict.update({"company": "A Company is already registered with this name."}) 
        
        user = User.objects.filter(email=email)

        if user:
            error_dict["email"] = "A user is already registered with this email."

        user = User.objects.filter(phone=phone)

        if user:
            error_dict["phone"] = "A user is already registered with this phone number."

        try:
            validate_password(data["password"])
        except ValidationError as e:
            error_dict["password"] = str(e)

        if not self.do_passwords_match(data["password"], confirmed_password):
            error_dict.update({"password": "passwords don't match"})

        if error_dict:
            raise ValidationError(error_dict)

        return data

    def create(self, validated_data):
        validated_data.pop("confirmed_password")
        user = self.Meta.create_user(**validated_data)
        return user
    

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

class VerifyUserSerializer(serializers.Serializer):

    token = serializers.CharField(required=True)

    def is_valid(self, raise_exception=False):
        super().is_valid(raise_exception)
        token = self.validated_data["token"]
        try:
            payload = decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        except DecodeError:
            raise ValidationError({"detail": "Invalid token"})
        user = get_object_or_404(User, email=payload["email"])
        user.is_verified = True
        user.save()


class InviteClientSerializer(serializers.Serializer):
    email = serializers.EmailField()


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


class UpdatePasswordSerializer(serializers.Serializer):

    confirm_password = serializers.CharField(validators=[validate_password])
    password = serializers.CharField(validators=[validate_password])
    token = serializers.CharField()

    def is_valid(self, raise_exception=True):
        super().is_valid(raise_exception=True)
        if not self.validated_data["confirm_password"] == self.initial_data["password"]:
            raise_validation_error({"detail":"Passwords do not match"})
        
        token = self.validated_data["token"]
        tokens = ResetPasswordToken.objects.filter(key=token)

        if not bool(tokens):
            raise_validation_error({"detail": "Invalid token"})

        if datetime.now() - tokens[0].created_at.replace(tzinfo=None)  > timedelta(hours=24):
            raise_validation_error({"detail": "Token expired"})

        

    def update_password(self):
        token = self.validated_data["token"]
        user = ResetPasswordToken.objects.get(key=token).user
        user.set_password(self.validated_data["password"])
        user.save()


class PasswordResetSerializer(serializers.Serializer):

    email = serializers.EmailField()

    def is_user_available(self):
        email = self.validated_data.get("email")
        users = User.objects.filter(email=email)
        return bool(users)

    def create(self, validated_data):
        email = validated_data.pop("email")
        user = User.objects.get(email=email)
        validated_data["user"] = user
        instance = ResetPasswordToken(**validated_data)
        instance.save()
        return instance


class CreateConsumerKeySerializer(serializers.ModelSerializer):

    def save(self, **kwargs):
        user = self.create_bot_user()
        self.validated_data["user"] = user
        super().save(**kwargs)

    def create_bot_user(self):
        email = fake.email()
        phone = "+254" + fake.msisdn()[:9]
        company = self.context["request"].user.company
        user = User.objects.create(full_name=self.validated_data["name"], email=email, company=company, phone=phone, is_verified=True, is_api_key_agent=True)

        return user


    class Meta:
        model = ConsumerKey
        fields = ["key", "id", "name"]
        extra_kwargs = {
            'user': {'read_only':True},
            'key': {'read_only':True}
            }

    
class KeyActivitySerializer(serializers.ModelSerializer):

    class Meta:
        model = APIKeyActivity
        fields = "__all__"

class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['full_name', 'phone', 'email', 'company']
        