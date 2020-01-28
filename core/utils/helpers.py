from django.db.utils import IntegrityError
from django.db import models
from rest_framework.exceptions import ValidationError


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
