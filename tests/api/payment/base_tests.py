import os

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from rest_framework.test import APIClient, APITestCase, APIRequestFactory
from rest_framework_simplejwt.views import TokenObtainPairView
from tests.factories.auth_factories import UserFactory
from rest_framework.test import force_authenticate
from api.sms import views
from . import dummy_data
from faker import Faker

fake = Faker()


class BaseTest(APITestCase):
    """Set up the testing client."""

    def setUp(self):
        self.client = APIClient()
        self.request_factory = APIRequestFactory()
        user = UserFactory.create()
        user.is_verified = True
        user.save()
        self.user = user
        self.create_list_sms_url = "/api/v1/sms/"
