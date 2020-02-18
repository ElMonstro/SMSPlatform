from unittest.mock import patch
from rest_framework import status
from rest_framework.test import force_authenticate

from .base_tests import BaseTest
from api.sms import views
from . import dummy_data


class TestGroup(BaseTest):
    def test_group_creation_succeeds(self):
        """Test that group creation with correct data will be successful"""
        request = self.request_factory.post(self.create_list_sms_url, dummy_data.valid_group_data)
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


class TestMembers(BaseTest):
    def test_create_member_creation_succeeds(self):
        """Test that group members creation with correct data will be successful"""
        data = dummy_data.valid_member_data.copy()
        data["group"] = self.group_id
        request = self.request_factory.post(self.create_list_sms_url, data)
        force_authenticate(request, self.user)
        response = views.GroupMembersView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_delete_group_members_succeeds(self):
        """Test that group members deletion successful"""
        data = dummy_data.valid_member_data.copy()
        data["group"] = self.group_id
        request = self.request_factory.post(self.create_list_sms_url, data)
        force_authenticate(request, self.user)
        response = views.GroupMembersView.as_view()(request)
        pk = response.data["id"]
        request = self.request_factory.delete(self.create_list_sms_url)
        force_authenticate(request, self.user)
        response = views.SingleGroupMembersView.as_view()(request, pk=pk)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_add_group_members_succeeds(self):
        """Test that add group members successful"""
        request = self.request_factory.post(self.create_list_sms_url, dummy_data.valid_group_data)
        force_authenticate(request, self.user)
        response = views.GroupView.as_view()(request)
        pk = response.data["id"]
        data = dummy_data.valid_member_data.copy()
        data["group"] = self.group_id
        request = self.request_factory.post(self.create_list_sms_url, data)
        force_authenticate(request, self.user)
        member_pk = views.GroupMembersView.as_view()(request).data["id"]
        data = {"members": [member_pk]}
        request = self.request_factory.patch(self.create_list_sms_url, data)
        force_authenticate(request, self.user)
        response = views.SingleGroupView.as_view()(request, pk=pk)
        self.assertEqual(member_pk, response.data["member_list"][0]["id"])

    def test_remove_group_members_succeeds(self):
        """Test that remove group members successful"""
        request = self.request_factory.post(self.create_list_sms_url, dummy_data.valid_group_data)
        force_authenticate(request, self.user)
        response = views.GroupView.as_view()(request)
        pk = response.data["id"]
        data = dummy_data.valid_member_data.copy()
        data["group"] = self.group_id
        request = self.request_factory.post(self.create_list_sms_url, data)
        force_authenticate(request, self.user)
        member_pk = views.GroupMembersView.as_view()(request).data["id"]
        data = {"members": [member_pk], "name": "name"}
        request = self.request_factory.patch(self.create_list_sms_url, data)
        force_authenticate(request, self.user)
        views.SingleGroupView.as_view()(request, pk=pk)
        request = self.request_factory.put(self.create_list_sms_url, data)
        force_authenticate(request, self.user)
        response = views.SingleGroupView.as_view()(request, pk=pk)
        self.assertEqual([], response.data["member_list"])
