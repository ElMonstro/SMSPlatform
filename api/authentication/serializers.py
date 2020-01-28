from rest_framework import serializers
from django.db.utils import IntegrityError
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from core.utils.validators import validate_phone_number
from core.utils.helpers import get_errored_integrity_field
from .models import User


class RegistrationSerializer(serializers.Serializer):
    """
    Serializer for handling user registration
    """

    email = serializers.EmailField()
    phone = serializers.CharField(required=False, validators=[validate_phone_number])
    full_name = serializers.CharField(max_length=100)
    role = serializers.CharField()
    password = serializers.CharField(max_length=124, min_length=8, write_only=True)
    confirmed_password = serializers.CharField(
        max_length=124, min_length=8, write_only=True
    )

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
            user = User.objects.create_user(**validated_data)
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
