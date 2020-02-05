from unittest.mock import patch
from rest_framework import status
from rest_framework.test import force_authenticate

from .base_tests import BaseTest
from api.sms import views
from . import dummy_data

class TestSMSTemplate(BaseTest):
    def test_create_sms_template_request_creation_succeeds(self):
        """Test that sms template creation with correct data will be successful"""
        request = self.request_factory.post(self.create_list_sms_url, dummy_data.valid_sms_template_data)
        force_authenticate(request, self.user)
        response = views.SMSTemplateView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_create_sms_template_request_fails_with_no_message_fails(self):
        """Test that sms template creation without group or receipient will fail"""
        request = self.request_factory.post(self.create_list_sms_url, dummy_data.invalid_sms_template_data)
        force_authenticate(request, self.user)
        response = views.SMSTemplateView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'][0], "This field is required.")

    def test_delete_sms_template_succeeds(self):
        """Test that sms template deletion succeeds"""
        request = self.request_factory.post(self.create_list_sms_url, dummy_data.valid_sms_template_data)
        force_authenticate(request, self.user)
        response = views.SMSTemplateView.as_view()(request)
        pk = response.data["id"]
        request = self.request_factory.delete(self.create_list_sms_url)
        force_authenticate(request, self.user)
        response = views.SingleSMSTemplateView.as_view()(request, pk=pk)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class TestGroup(BaseTest):
    def test_create_group_creation_succeeds(self):
        """Test that group creation with correct data will be successful"""
        request = self.request_factory.post(self.create_list_sms_url, dummy_data.valid_sms_template_data)
        force_authenticate(request, self.user)
        response = views.GroupView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_delete_group_succeeds(self):
        """Test that group deletion successful"""
        request = self.request_factory.post(self.create_list_sms_url, dummy_data.valid_group_data)
        force_authenticate(request, self.user)
        response = views.GroupView.as_view()(request)
        pk = response.data["id"]
        request = self.request_factory.delete(self.create_list_sms_url)
        force_authenticate(request, self.user)
        response = views.SingleGroupView.as_view()(request, pk=pk)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
