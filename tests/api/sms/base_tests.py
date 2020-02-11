from django.urls import reverse
from rest_framework.test import APIClient, APITestCase, APIRequestFactory
from rest_framework_simplejwt.views import TokenObtainPairView
from tests.factories.auth_factories import UserFactory
from faker import Faker

fake = Faker()


class BaseTest(APITestCase):
    """Set up the testing client."""

    def setUp(self):
        self.client = APIClient()
        self.request_factory = APIRequestFactory()
        self.user = UserFactory.create()
        self.create_list_sms_url = "/api/v1/sms/"
