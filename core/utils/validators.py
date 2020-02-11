import re
from rest_framework.exceptions import ValidationError


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

    regex_pattern = r"^\+\d{1,3}\d{3,}$"

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

def validate_primary_keys(keys):
    invalid_keys = []
    for key in keys:
        if not isinstance(key, int):
            invalid_keys.append(key)
    if invalid_keys:
        raise ValidationError({"detail": f"Only integers allowed. {str(invalid_keys)[1:-1]} is/are invalid."})

def validate_model_reference_is_own(user, model, instance):
    """Validate the user owns the group reference"""
    if not instance.owner == user:
        raise ValidationError({"detail": "The group referenced is not owned by the current user"})
