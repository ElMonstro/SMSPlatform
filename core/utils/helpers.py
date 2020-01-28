from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError


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
    field = exc_message[exc_message.find("(")+1:exc_message.find(")")]

    return field if field else None
