from rest_framework.test import APIClient, APITestCase
from django.urls import reverse
from tests.factories.auth_factories import UserFactory
from faker import Faker

fake = Faker()


class BaseTest(APITestCase):
    """Set up the testing client."""

    def setUp(self):
        self.client = APIClient()
        self.registration_url = "/api/v1/auth/register/"
        self.user = UserFactory.create()
        self.new_user = {
            "full_name": self.user.full_name,
            "email": fake.email(),
            "password": self.user.password,
            "confirmed_password": self.user.password,
            "role": self.user.role.title,
            "phone": "+254" + fake.msisdn()[:9],
        }

        self.umatching_passwords_data = {
            "full_name": self.user.full_name,
            "email": self.user.email + "s",
            "password": self.user.password,
            "confirmed_password": self.user.password + "v",
            "role": self.user.role.title,
            "phone": "+254" + fake.msisdn()[:9],
        }
        self.invalid_email_data = {
            "full_name": self.user.full_name,
            "email": self.user.email.replace("@", ""),
            "password": self.user.password,
            "confirmed_password": self.user.password,
            "role": self.user.role.title,
            "phone": "+254" + fake.msisdn()[:9],
        }

        self.no_role_field_data = {
            "full_name": self.user.full_name,
            "email": self.user.email + "p",
            "password": self.user.password,
            "confirmed_password": self.user.password,
            "phone": "+254" + fake.msisdn()[:9],
        }

        self.weak_password_data = {
            "full_name": self.user.full_name,
            "email": self.user.email + "m",
            "password": "123456",
            "confirmed_password": self.user.password,
            "role": self.user.role.title,
            "phone": "+254" + fake.msisdn()[:9],
        }
        self.number_in_first_name_data = {
            "full_name": self.user.full_name,
            "email": self.user.email + "s",
            "password": self.user.password,
            "confirmed_password": self.user.password,
            "role": self.user.role.title,
            "phone": "+254" + fake.msisdn()[:9],
        }

        self.empty_full_name_data = {
            "full_name": "",
            "email": self.user.email + "s",
            "password": self.user.password,
            "confirmed_password": self.user.password,
            "role": self.user.role.title,
            "phone": "+254" + fake.msisdn()[:9],
        }


        self.invalid_phone = {
            "full_name": self.user.full_name,
            "email": self.user.email + "m",
            "password": self.user.password,
            "confirmed_password": self.user.password,
            "role": self.user.role.title,
            "phone": "4352",
        }
