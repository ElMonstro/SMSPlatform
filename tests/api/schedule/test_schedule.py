from unittest.mock import patch
from rest_framework import status
from rest_framework.test import force_authenticate

from .base_tests import BaseTest
from api.schedule import views, models
from api.sms import models
from . import dummy_data


class TestRecharge(BaseTest):

    def test_register_schedule_succeeds(self):
        """Test register schedule with correct data will be successful"""
        data = dummy_data.schedule_data.copy()
        instance = models.SMSGroup(name='group', company=self.user.company)
        instance.save()
        data["group"] = instance.id
        request = self.request_factory.post(self.create_list_sms_url, data)
        force_authenticate(request, self.user)
        response = views.CreateScheduleView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_schedule_succeeds(self):
        """Test update schedule with correct data will be successful"""
        data = dummy_data.schedule_data.copy()
        instance = models.SMSGroup(name='group', company=self.user.company)
        instance.save()
        data["group"] = instance.id
        request = self.request_factory.post(self.create_list_sms_url, data)
        force_authenticate(request, self.user)
        response = views.CreateScheduleView.as_view()(request)
        id = response.data["id"]
        request = self.request_factory.patch(self.create_list_sms_url, data)
        force_authenticate(request, self.user)
        response = views.RetrieveUpdateScheduleView.as_view()(request, pk=id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    