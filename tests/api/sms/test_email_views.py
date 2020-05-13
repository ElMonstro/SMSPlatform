from unittest.mock import patch
from rest_framework import status
from rest_framework.test import force_authenticate

from .base_tests import BaseTest
from api.sms import views, models
from . import dummy_data


class EmailRequestViewsTest(BaseTest):
    """Test Email request creation list and deletion"""
    @patch("api.sms.serializers.send_mail")
    def test_sms_request_creation_succeeds(self, _):
        """Test that email creation with correct data will be successful"""
        request = self.request_factory.post(self.create_list_sms_url + '?medium=email', dummy_data.valid_email_data)
        force_authenticate(request, self.user)
        response = views.SMSRequestView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_create_email_request_fails_with_no_group_or_recepients_fails(self):
        """Test that email creation without group or receipient will fail"""
        request = self.request_factory.post(self.create_list_sms_url + '?medium=email', dummy_data.email_data_without_recepient_or_group)
        force_authenticate(request, self.user)
        response = views.SMSRequestView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], "A receipient group id or a recepient contact list must be provided")

    @patch("api.sms.serializers.send_mail")
    def test_create_email_request_with_both_group_or_recepients_succeeds(self, _):
        """Test that email creation with both group or receipient will succeed"""
        email_group = models.EmailGroup.objects.create(name="tuskys", company=self.user.company)
        dummy_data.email_data_with_both_recepient_or_group["groups"] = [email_group.pk]
        request = self.request_factory.post(self.create_list_sms_url + '?medium=email', dummy_data.email_data_with_both_recepient_or_group)
        force_authenticate(request, self.user)
        instance = models.EmailGroupMember.objects.create(email=self.user.email, company=self.user.company)
        email_group.members.add(instance)
        email_group.save()
        response = views.SMSRequestView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_email_request_group_with_no_recepients_fails(self):
        """Test that email creation with group with no members fails"""
        email_group = models.EmailGroup.objects.create(name="tuskys", company=self.user.company)
        dummy_data.email_data_with_both_recepient_or_group["groups"] = [email_group.pk]
        request = self.request_factory.post(self.create_list_sms_url + '?medium=email', dummy_data.email_data_with_both_recepient_or_group)
        force_authenticate(request, self.user)
        response = views.SMSRequestView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], "There are no members in the specified group(s)")


    @patch("api.sms.serializers.send_mail")
    def test_get_email_requests_succeeds(self, _):
        """Test that get created email succeed"""
        request = self.request_factory.get(self.create_list_sms_url + '?medium=email')
        force_authenticate(request, self.user)
        instance = models.EmailRequest.objects.create(company=self.user.company,**dummy_data.valid_email_data)
        response = views.SMSRequestView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual((response.data)['results'][0]["id"], instance.pk)

    @patch("api.sms.serializers.send_mail")
    def test_delete_email_requests_valid_data_succeeds(self, _):
        """Test that delete created email succeed"""
        instance = models.EmailRequest.objects.create(company=self.user.company, **dummy_data.valid_email_data)
        id = instance.pk
        delete_request = self.request_factory.delete(self.create_list_sms_url + '?medium=email', {"message_requests": [id]})
        force_authenticate(delete_request, self.user)
        response = views.SMSRequestView.as_view()(delete_request)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_email_requests_non_existent_id_fails(self):
        """Test that delete email requests  with non-existent id fails"""
        delete_request = self.request_factory.delete(self.create_list_sms_url + '?medium=email', {
                            "message_requests": [100]
                        })
        force_authenticate(delete_request, self.user)
        response = views.SMSRequestView.as_view()(delete_request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message_requests"][0], ['Invalid pk "100" - object does not exist.'])
