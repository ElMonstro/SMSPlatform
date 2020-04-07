import os

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from rest_framework.test import APIClient, APITestCase, APIRequestFactory
from rest_framework_simplejwt.views import TokenObtainPairView
from tests.factories.auth_factories import UserFactory
from rest_framework.test import force_authenticate
from api.sms import views, models
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
        instance = models.SMSGroup(name="name", company=self.user.company)
        instance.save()
        self.group_instance = instance
        self.group_id = instance.pk

class UploadBasetest(BaseTest):
    """setup csv tests"""
    def setUp(self):
        super().setUp()
        

    @staticmethod
    def create_upload_file(file_name):

        base_path = os.path.dirname(os.path.realpath(__file__))
        with open(base_path + '/' + file_name, 'rb') as file:
            file = SimpleUploadedFile(content = file.read(),name = file.name,content_type='multipart/form-data')

        content_type = 'multipart/form-data'
        headers = {
        'HTTP_CONTENT_TYPE': content_type,
        'HTTP_CONTENT_DISPOSITION': 'attachment; filename=' + file_name}
        return (file, headers)

