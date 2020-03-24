import re

from django.db.utils import IntegrityError
from django.db import models
from rest_framework.exceptions import ValidationError
import pandas as pd
import re


def get_errored_integrity_field(exc):
    """
    Accept an instance of an integrity error and return the field that is causing the error.
    """

    if not isinstance(exc, IntegrityError):
        pass

    # example of Integrity error string:
    # 'duplicate key value violates unique constraint
    # "authentication_user_passport_number_key"\nDETAIL:  Key (passport_number)
    # (3452345) already exists.\n'

    # Find the index of `Key` and slice our string so that we get the field.

    key_index = exc.args[0].find("Key")

    exc_message = exc.args[0][key_index:]

    # the field is between the first pair of brackets after our message.
    field = exc_message[exc_message.find("(") + 1 : exc_message.find(")")]
    field = field.split(' ')[-1]

    return field if field else None


def soft_delete_owned_object(model, user, pk):
    """
    soft deletes and object if the user owns it
    params:
        model - django model
        user - user object
        pk - object primary key
    returns: None
    Raises:
        Validation error if primary key is not an integer
    """
    try:
        sms_request = model.active_objects.get(pk=pk, owner=user)
        sms_request.soft_delete(commit=True)
    except models.ObjectDoesNotExist:
        pass
    except (ValueError, TypeError):
        raise ValidationError({"detail": f"Only integers allowed. '{pk}' is invalid."})


class CsvExcelReader:
    """
    A class that is initialized with a csv or excel file another which is 
    read and data placed in the data property
    """
    def __init__(self, file, required_headers):
        self.data = None
        self.file = file
        self.required_headers = required_headers
        self.read_file()
        self.validate_headers()

    def read_csv(self):
        self.data = pd.read_csv(self.file).drop_duplicates(subset=self.required_headers, keep="first")
    def read_excel(self):
        self.data = pd.read_excel(self.file).drop_duplicates(subset=self.required_headers, keep="first")
    
    def read_file(self):
        read_file = {
            "csv": self.read_csv,
            "xls": self.read_excel,
            "xlsx": self.read_excel
        }
        ext = self.file.name.split(".")[-1]
        read_file[ext]()
        self.data
    
    def validate_headers(self):
        headers = sorted(self.data)
        valid = all(value in headers for value in self.required_headers)
        if not valid:
            raise ValidationError({"detail": "The file does not have all the required column headers," \
                + f"make sure it has the following headers: {str(self.required_headers)[1:-1]} "})


def add_country_code(number):
    """
    Checks if number has the the country code and add it
    """
    if number == 'nan':
        raise ValidationError()
    regex_pattern = r"^\+\d{3}\d{9}$"
    number = str(int(float(number)))
    match = re.search(regex_pattern, number)
    if match:
        return number
    regex_pattern = r"^\d{9}$"
    match = re.match(regex_pattern, number)
    if match:
        return "+254" + number
    else:
        raise ValidationError()


def camel_to_snake(name):
    """Convert camelcase names to snake case"""
    pattern = re.compile(r'(?<!^)(?=[A-Z])')
    name = pattern.sub('_', name).lower()
    return name

def raise_validation_error(message=None):
    raise ValidationError(message)
    