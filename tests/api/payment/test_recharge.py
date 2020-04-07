from datetime import datetime, timedelta
from unittest.mock import patch
from rest_framework import status
from rest_framework.test import force_authenticate

from .base_tests import BaseTest
from api.payment import views, models
from . import dummy_data

class TestRecharge(BaseTest):


    @patch("api.payment.serializers.send_LNM_request")
    def test_send_recharge_request_succeeds(self, _):
        """Test recharge view with correct data will be successful"""
        request = self.request_factory.post(self.create_list_sms_url, dummy_data.recharge_data)
        force_authenticate(request, self.user)
        response = views.RechargeView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_send_recharge_request_fails_with_incorrect_data(self):
        """Test recharge view without customer number  will fail"""
        data = dummy_data.recharge_data.copy()
        data.pop("customer_number")
        request = self.request_factory.post(self.create_list_sms_url, data)
        force_authenticate(request, self.user)
        response = views.RechargeView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        

class TestMpesaCallBack(BaseTest):
    
    @patch("api.payment.serializers.send_sms")
    def test_receive_valid_mpesa_callback_request_succeeds(self, _):
        """Test that a valid mpesa callback will pass"""
        models.RechargeRequest(company=self.user.company, customer_number="254726406930", checkout_request_id="fwer544tgre", response_code=0).save()
        models.RechargePlan(name="ting", rate=0.50, price_limit=5).save()
        data = dummy_data.mpesa_callback.copy()
        transaction_date = (datetime.now() + timedelta(hours=3, seconds=60)).replace(tzinfo=None)
        data["Body"]["stkCallback"]["CallbackMetadata"]["Item"][3]["Value"] = transaction_date.strftime("%Y%m%d%H%M%S")
        request = self.request_factory.post(self.create_list_sms_url, data, format='json')
        response = views.MpesaCallbackView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


    def test_receive_invalid_mpesa_callback_request_fails(self):
        """Test receive invalid mpesa callback request fails"""
        models.RechargeRequest(company=self.user.company, customer_number="254726406930", checkout_request_id="fwer544tgre", response_code=0).save()
        models.RechargePlan(name="ting", rate=0.50, price_limit=5).save()
        data = dummy_data.mpesa_callback.copy()
        transaction_date = (datetime.now() + timedelta(hours=4, seconds=60)).replace(tzinfo=None)
        data["Body"]["stkCallback"]["CallbackMetadata"]["Item"][3]["Value"] = transaction_date.strftime("%Y%m%d%H%M%S")
        request = self.request_factory.post(self.create_list_sms_url, data, format='json')
        response = views.MpesaCallbackView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Invalid request")


class TestRecharPlanViews(BaseTest):


    def test_send_recharge_plan_request_succeeds(self):
        """Test recharge plan view with correct data will be successful"""
        request = self.request_factory.post(self.create_list_sms_url, dummy_data.recharge_plan_data)
        self.user.is_superuser = True
        self.user.save()
        force_authenticate(request, self.user)
        response = views.CreateListRechargePlanView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_send_recharge_plan_request_fails_with_incorrect_data(self):
        """Test recharge view without customer number will fail"""
        self.user.is_superuser = True
        self.user.save()
        data = dummy_data.recharge_plan_data.copy()
        data.pop("price_limit")
        request = self.request_factory.post(self.create_list_sms_url, data)
        force_authenticate(request, self.user)
        response = views.CreateListRechargePlanView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["price_limit"][0], "This field is required.")


class TestGetPaymentsView(BaseTest):

    @patch("api.payment.serializers.send_sms")
    def test_get_payments_request_succeeds(self, _):
            """Test that a valid mpesa callback will pass"""
            models.RechargeRequest(company=self.user.company, customer_number="254726406930", checkout_request_id="fwer544tgre", response_code=0).save()
            models.RechargePlan(name="ting", rate=0.50, price_limit=5).save()
            data = dummy_data.mpesa_callback.copy()
            transaction_date = (datetime.now() + timedelta(hours=3, seconds=60)).replace(tzinfo=None)
            data["Body"]["stkCallback"]["CallbackMetadata"]["Item"][3]["Value"] = transaction_date.strftime("%Y%m%d%H%M%S")
            request = self.request_factory.post(self.create_list_sms_url, data, format='json')
            views.MpesaCallbackView.as_view()(request)
            request = self.request_factory.get(self.create_list_sms_url)
            force_authenticate(request, self.user)
            response = views.PaymentListView.as_view()(request)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["results"][0]["mpesa_receipt_number"], data["Body"]["stkCallback"]["CallbackMetadata"]["Item"][1]["Value"])
