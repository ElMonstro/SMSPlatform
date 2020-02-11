from unittest.mock import patch
from rest_framework import status
from rest_framework.test import force_authenticate

from .base_tests import BaseTest
from api.sms import views
from . import dummy_data


class SMSRequestViewsTest(BaseTest):
    """Test SMS request creation list and deletion"""
    @patch("api.sms.serializers.send_sms")
    def test_create_sms_request_creation_succeeds(self, _):
        """Test that sms creation with correct data will be successful"""
        request = self.request_factory.post(self.create_list_sms_url, dummy_data.valid_sms_data)
        force_authenticate(request, self.user)
        response = views.SMSRequestView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_create_sms_request_fails_with_no_group_or_recepients_fails(self):
        """Test that sms creation without group or receipient will fail"""
        request = self.request_factory.post(self.create_list_sms_url, dummy_data.data_without_recepient_or_group)
        force_authenticate(request, self.user)
        response = views.SMSRequestView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], "A receipient group id or a recepient phone number list must be provided")

    def test_create_sms_request_fails_with_both_group_or_recepients_fails(self):
        """Test that sms creation with bothc group or receipient will fail"""
        request = self.request_factory.post(self.create_list_sms_url, dummy_data.data_with_both_recepient_or_group)
        force_authenticate(request, self.user)
        response = views.SMSRequestView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], "Either send group id or receipient list not both")

    @patch("api.sms.serializers.send_sms")
    def test_get_sms_requests_succeeds(self, _):
        """Test that get created sms succeed"""
        request = self.request_factory.post(self.create_list_sms_url, dummy_data.valid_sms_data)
        get_request = self.request_factory.get(self.create_list_sms_url)
        force_authenticate(request, self.user)
        force_authenticate(get_request, self.user)
        views.SMSRequestView.as_view()(request)
        response = views.SMSRequestView.as_view()(get_request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual((response.data)['results'][0]["message"], dummy_data.valid_sms_data["message"])

    @patch("api.sms.serializers.send_sms")
    def test_delete_sms_requests_valid_data_succeeds(self, _):
        """Test that delete created sms succeed"""
        create_request = self.request_factory.post(self.create_list_sms_url, dummy_data.valid_sms_data)
        get_request = self.request_factory.get(self.create_list_sms_url)
        force_authenticate(create_request, self.user)
        force_authenticate(get_request, self.user)
        views.SMSRequestView.as_view()(create_request)
        id = views.SMSRequestView.as_view()(get_request).data['results'][0]["id"]
        delete_request = self.request_factory.delete(self.create_list_sms_url, {"sms_requests": [id]})
        force_authenticate(delete_request, self.user)
        response = views.SMSRequestView.as_view()(delete_request)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_sms_requests_non_existent_id_succeeds(self):
            """Test that delete sms requests  with non-existent id  succeeds"""
            delete_request = self.request_factory.delete(self.create_list_sms_url, {
                                "sms_requests": [100]
                            })
            force_authenticate(delete_request, self.user)
            response = views.SMSRequestView.as_view()(delete_request)
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
