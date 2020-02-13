from rest_framework import status
from rest_framework.test import force_authenticate
from unittest.mock import patch

from .base_tests import BaseTest
from api.authentication import views


class UserRegistrationTest(BaseTest):
    """Contains user registration test methods."""

    def test_user_should_register(self):
        """Create an account."""
        response = self.client.post(self.registration_url, self.new_user, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_should_not_register_with_invalid_email(self):
        """Create an account with an invalid email."""
        response = self.client.post(
            self.registration_url, self.invalid_email_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["email"][0], "Enter a valid email address.")

    def test_user_should_not_register_with_a_taken_email(self):
        """Create an account with a taken email"""
        self.client.post(self.registration_url, self.new_user, format="json")
        response = self.client.post(self.registration_url, self.new_user, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["email"], "A user is already registered with this email."
        )

    def test_user_should_not_register_with_a_weak_password(self):
        """Create an account with a weak password."""
        response = self.client.post(
            self.registration_url, self.weak_password_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNotNone(response.data["password"])

    def test_user_should_not_register_with_unmatching_passwords(self):
        """Create an account with passwords that donot match."""
        response = self.client.post(
            self.registration_url, self.umatching_passwords_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNotNone(response.data["password"])

    def test_user_should_not_register_with_invalid_phone_no(self):
        """Create an account with invalid phone no."""
        response = self.client.post(
            self.registration_url, self.invalid_phone, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNotNone(response.data["phone"])


class StaffRegistrationTest(BaseTest):
    """Contains user registration test methods."""

    def test_staff_register(self):
        """Create staff account."""
        response = self.client.post(self.registration_url + '?user=staff', self.staff, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @patch("api.authentication.models.send_mail")
    def test_add_staff(self, _):
        """Test Add staff."""
        data = {"email": "jratcher@gmail.com"}
        request = self.request_factory.post(self.registration_url, data)
        self.user.is_admin = True
        force_authenticate(request, self.user)
        response = views.AddStaffView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
