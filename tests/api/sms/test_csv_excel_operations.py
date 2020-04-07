from unittest.mock import patch
from rest_framework import status
from rest_framework.test import force_authenticate
from rest_framework.test import APIClient

from .base_tests import UploadBasetest
from api.sms import views
from . import dummy_data

class TestCsvExcel(UploadBasetest):
    def test_csv_upload_group_members_succeeds(self):
        """Test that group members can be uploaded from correct csv data will be successful"""
        file, headers = self.create_upload_file('csv.csv')
        data = {
            "file": file,
            "group": self.group_id
        }

        request = self.request_factory.post(self.create_list_sms_url, data, **headers)
        force_authenticate(request, self.user)
        response = views.MassMemberUploadView.as_view()(request)
        self.assertEqual(response.data["members"][0]["phone"], '+254726406913')
        self.assertTrue(response.data["skipped_lines"])
    
    def test_excel_upload_group_members_succeeds(self):
        """Test that group members can be uploaded from correct excel data will be successful"""
        file, headers = self.create_upload_file('excel.xlsx')
        data = {
            "file": file,
            "group": self.group_id
        }

        request = self.request_factory.post(self.create_list_sms_url, data, **headers)
        force_authenticate(request, self.user)
        response = views.MassMemberUploadView.as_view()(request)
        self.assertEqual(response.data["members"][0]["phone"], '+254724056913')

    @patch("api.sms.serializers.send_sms")
    def test_csv_upload_sms_succeeds(self, _):
        """Test that sms can be sent can be uploaded from correct csv data will be successful"""
        file, headers = self.create_upload_file('csv.csv')
        data = {
            "file": file,
            "message": "yoh"
        }

        request = self.request_factory.post(self.create_list_sms_url, data, **headers)
        force_authenticate(request, self.user)
        response = views.CsvSmsView.as_view()(request)
        self.assertTrue(response.data["recepients"][0])

    @patch("api.sms.serializers.send_sms")
    def test_csv_upload_personalized_sms_succeeds(self, _):
        """Test that sms sent from correct csv data will be successful"""
        file, headers = self.create_upload_file('csv.csv')
        data = {
            "file": file,
            "message": "come mbio",
            "greeting_text": "Yoh"
        }

        request = self.request_factory.post(self.create_list_sms_url + '?sms=personalized', data, **headers)
        force_authenticate(request, self.user)
        response = views.CsvSmsView.as_view()(request)
        self.assertTrue(response.data["recepients"][0])

    @patch("api.sms.serializers.send_mass_unique_sms")
    @patch("api.sms.serializers.send_sms")
    def test_csv_upload_personalized_sms_fails_with_no_greeting_text (self, _, __):
        """Test that sms can be sent correct csv data will fail"""
        file, headers = self.create_upload_file('csv.csv')
        data = {
            "file": file,
            "message": "come mbio",
        }

        request = self.request_factory.post(self.create_list_sms_url + '?sms=personalized', data, **headers)
        force_authenticate(request, self.user)
        response = views.CsvSmsView.as_view()(request)
        self.assertEqual(response.data["greeting_text"], 'There must be a greeting message for personalized messages')
        self.assertEqual(response.status_code, 400)

