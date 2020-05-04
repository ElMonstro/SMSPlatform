from api.authentication.models import ConsumerKey
from rest_framework import authentication
from rest_framework import exceptions

from core.utils.helpers import log_api_key_request
from api.authentication.models import APIKeyActivity


class ConsumerKeyAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        consumer_key = request.META.get('HTTP_CONSUMER_KEY')
        if not consumer_key:
            return None
        try:
            consumer_key = ConsumerKey.objects.get(key=consumer_key)
        except ConsumerKey.DoesNotExist:
            return None

        log_api_key_request(APIKeyActivity, consumer_key.user.company, consumer_key, request.path, request.META['REQUEST_METHOD'])

        return (consumer_key.user, None)
