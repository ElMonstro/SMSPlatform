from datetime import datetime
from django.urls import reverse
from django.conf import settings
from rest_framework.test import APIClient, APITestCase, APIRequestFactory
from tests.factories.auth_factories import UserFactory
from faker import Faker
from jwt import encode

fake = Faker()


class BaseTest(APITestCase):
    """Set up the testing client."""

    def setUp(self):
        self.client = APIClient()
        self.registration_url = "/api/v1/auth/register/"
        self.request_factory = APIRequestFactory()
        self.user = UserFactory.create()
        self.new_user = {
            "full_name": self.user.full_name,
            "email": fake.email(),
            "password": self.user.password,
            "confirmed_password": self.user.password,       
            "phone": "+254" + fake.msisdn()[:9],
            "company": fake.msisdn()[:9],
            "county": "Nairobi"
        }

        payload = { 
            "email": fake.email(),
            "company": self.user.company.name,
            "date": datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
             }
        token = encode(payload, settings.SECRET_KEY)

        self.staff = {
            "full_name": self.user.full_name,
            "password": self.user.password,
            "confirmed_password": self.user.password,       
            "phone": "+254" + fake.msisdn()[:9],
            "token": token
        }

        self.umatching_passwords_data = {
            "full_name": self.user.full_name,
            "email": self.user.email + "s",
            "password": self.user.password,
            "confirmed_password": self.user.password + "v",
            "phone": "+254" + fake.msisdn()[:9],
            "company": "Company",
            "county": "Nairobi"
        }
        self.invalid_email_data = {
            "full_name": self.user.full_name,
            "email": self.user.email.replace("@", ""),
            "password": self.user.password,
            "confirmed_password": self.user.password,
            "phone": "+254" + fake.msisdn()[:9],
            "company": "Company",
            "county": "Nairobi"
        }

        self.no_company_field_data = {
            "full_name": self.user.full_name,
            "email": self.user.email + "p",
            "password": self.user.password,
            "confirmed_password": self.user.password,
            "phone": "+254" + fake.msisdn()[:9],
            "county": "Nairobi"
        }

        self.weak_password_data = {
            "full_name": self.user.full_name,
            "email": self.user.email + "m",
            "password": "123456",
            "confirmed_password": self.user.password,
            "phone": "+254" + fake.msisdn()[:9],

        }
        self.number_in_first_name_data = {
            "full_name": self.user.full_name,
            "email": self.user.email + "s",
            "password": self.user.password,
            "confirmed_password": self.user.password,
            "phone": "+254" + fake.msisdn()[:9],
        }

        self.empty_full_name_data = {
            "full_name": "",
            "email": self.user.email + "s",
            "password": self.user.password,
            "confirmed_password": self.user.password,
            "company": "Company",
            "phone": "+254" + fake.msisdn()[:9],
        }


        self.invalid_phone = {
            "full_name": self.user.full_name,
            "email": self.user.email + "m",
            "password": self.user.password,
            "confirmed_password": self.user.password, 
            "phone": "4352",
            "company": "Company",
            "county": "Nairobi"
        }
