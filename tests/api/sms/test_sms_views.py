from unittest.mock import patch
from rest_framework import status
from rest_framework.test import force_authenticate

from .base_tests import BaseTest
from api.sms import views, models
from . import dummy_data


class SMSRequestViewsTest(BaseTest):
    """Test SMS request creation list and deletion"""
    @patch("api.sms.serializers.send_sms")
    def test_sms_request_creation_succeeds(self, _):
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
        self.assertEqual(response.data['detail'], "A receipient group id or a recepient contact list must be provided")

    @patch("api.sms.serializers.send_sms")
    def test_create_sms_request_with_both_group_or_recepients_succeeds(self, _):
        """Test that sms creation with both group or receipient will succeed"""
        dummy_data.data_with_both_recepient_or_group["groups"] = [self.group_id]
        request = self.request_factory.post(self.create_list_sms_url, dummy_data.data_with_both_recepient_or_group)
        force_authenticate(request, self.user)
        instance = models.GroupMember(phone=self.user.phone, company=self.user.company)
        instance.save()
        self.group_instance.members.add(instance)
        self.group_instance.save()
        response = views.SMSRequestView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

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
        instance = models.SMSRequest(company=self.user.company, recepients=["+254726406733"], message="Come")
        instance.save()
        id = instance.pk
        delete_request = self.request_factory.delete(self.create_list_sms_url, {"message_requests": [id]})
        force_authenticate(delete_request, self.user)
        response = views.SMSRequestView.as_view()(delete_request)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_sms_requests_non_existent_id_fails(self):
        """Test that delete sms requests  with non-existent id fails"""
        delete_request = self.request_factory.delete(self.create_list_sms_url, {
                            "message_requests": [100]
                        })
        force_authenticate(delete_request, self.user)
        response = views.SMSRequestView.as_view()(delete_request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message_requests"][0], ['Invalid pk "100" - object does not exist.'])

    def test_create_brand_name_succeeds(self):
        """Test that brand name is created with correct data"""
        request = self.request_factory.post(self.create_list_sms_url, {
                            "name": "Branded"
                        })
            
        force_authenticate(request, self.user)
        response = views.CreateBrandName.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_brand_names_succeeds(self):
        """Test list brand name request """
        request = self.request_factory.get(self.create_list_sms_url)
        self.user.is_superuser = True
        self.user.save()
        instance = models.SMSBranding.objects.create(name="create", company=self.user.company)
        force_authenticate(request, self.user)
        response = views.ListBrandNameRequests.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["id"], instance.pk)

    def test_edit_brand_names_succeeds(self):
        """Test edit brand name request"""
        request = self.request_factory.patch(self.create_list_sms_url, {"is_approved": True})
        self.user.is_superuser = True
        self.user.save()
        instance = models.SMSBranding.objects.create(name="create", company=self.user.company)
        force_authenticate(request, self.user)
        response = views.EditBrandNameRequests.as_view()(request, pk=instance.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["is_approved"], True)
