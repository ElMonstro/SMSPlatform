from decimal import Decimal
import re

from rest_framework.exceptions import ValidationError
from .helpers import add_country_code, raise_validation_error

TRANSACTION_DESCRIPTIONS = ["brand_payment", "sms_topup"]

def validate_passed_file_extension(extension):
    """returns a validator for the passed extension"""

    def validator(value):
        ext = value.name.split(".")[-1]
        if not ext.lower() == extension:
            raise ValidationError(f"This is not a {extension} file.")

    return validator


def validate_phone_number(phone):
    """
    Validate an phone number.
    - Number must contain no spaces
    - Number must be of correct length
    - Number must have no letters

    https://support.twilio.com/hc/en-us/articles/223183008-Formatting-International-Phone-Numbers

    return True if number is valid. False otherwise.
    """

    regex_pattern = r"^\+\d{3}\d{9}$"

    match = re.search(regex_pattern, phone)

    if not match:
        return False
    return True


def validate_required_arguments(kwargs, required_args):
    """
    This function takes a dictionary that contains arguments and their values. The second parameter is a list or tuple which contains arguments that:
        - Must be present in kwargs.
        - Must be truthy

    Consider I have a function that accepts keyword arguments.
        f(a=None, b=None, c=None):
            pass
    If all keyword arguments should be truthy at runtime, we would have to
    create loops to check if each condition is truthy:
        ...
        if not a:
            raise Exception
        ...etc

    This function loops through the passed kwargs(dict) and ensures that they are not empty and that they are truthy.
    returns kwargs or raises Django Validation Error.
    """

    for arg in required_args:
        if arg not in kwargs.keys():  # arg must be present
            raise ValidationError({arg: "This field is required."})
        elif not kwargs.get(arg):  # arg must be truthy
            raise ValidationError({arg: "This field cannot be empty."})
    return kwargs


def validate_phone_list(phone_list):
    """Loops through and validates phone numbers"""
    if len(phone_list) > 5:
        raise ValidationError(
            "Recepeints more than five, use bulk SMS or group features instead"
        )
    for index, number in enumerate(phone_list):
        if not validate_phone_number(number):
            raise ValidationError(f"Invalid phone number at index {index}")


def validate_model_reference_is_own(user, model, instance):
    """Validate the user owns the group reference"""
    if not instance.owner == user:
        raise ValidationError({"detail": "The group referenced is not owned by the current user"})


def validate_excel_csv(file):
    """
    Validate csv or excel files
    """
    ext = file.name.split(".")[-1]
    regex_pattern = r"^(xls|xlsx|csv)$"

    match = re.match(regex_pattern, ext)
    if not match:
        raise ValidationError("File type invalid, please upload csv or excel files")
    return True


def get_intnl_phone(serializer):
    try:
        intnl_phone = add_country_code(serializer.validated_data["phone"])
    except ValidationError:
        return
    return intnl_phone

def validate_csv_row(serializer):
    try:
        serializer.is_valid(raise_exception=True)
    except ValidationError:
        return 
    return get_intnl_phone(serializer)

def validate_first_name_column(first_name):
    if first_name == 'nan':
        raise ValidationError()

def validate_mpesa_phone_number(phone):
    """
    Validate mpesa phone number.
    - Number must contain no spaces
    - Number must be of correct length
    - Number must have no letters

    https://support.twilio.com/hc/en-us/articles/223183008-Formatting-International-Phone-Numbers

    return True if number is valid. False otherwise.
    """

    regex_pattern = r"^254\d{9}$"

    match = re.search(regex_pattern, phone)

    if not match:
        return False
    return True


def transaction_description_validator(transaction_desc):
    """
    Validates if a transaction description is valid
    """
    if not transaction_desc in TRANSACTION_DESCRIPTIONS:
        raise ValidationError(f"Invalid transaction description use: {str(TRANSACTION_DESCRIPTIONS)[1:-1]}")


def validate_if_branding_fee_is_set(queryset):
    """
    Validates that transaction fee is created
    """
    if not queryset:
        raise_validation_error({"detail": "Branding fee not set, contact JamboSMS admin"})


def validate_branding_fee(fee, amount):
    """
    Validate amount is same as branding fee
    """
    if not fee == Decimal(amount):
        raise_validation_error({"detail": "The payment is not the same as the branding fee"})
