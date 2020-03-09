import requests
import os
import base64
import json
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta

from django.conf import settings
from django.core.cache import cache

from django_celery_beat.models import CrontabSchedule, PeriodicTask

from jamboSms.celery import app
from api.payment.models import RechargeRequest
from .helpers import camel_to_snake, raise_validation_error



class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token
    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        r.headers["Content-Type"] = "application/json"
        return r


class MpesaHandler:
    """Handle Mpesa requests"""
    def __init__(self, customer_number=None, amount=None, transaction_desc="test"):
       self.amount = amount
       self.customer_number = customer_number
       self.transaction_desc = transaction_desc
       self.payload = {}

    def create_LNM_payload(self):
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        business_shortcode = settings.MPESA_BUSINESS_SHORTCODE
        lnm_passkey = settings.MPESA_LNM_PASSKEY
        call_back_url = settings.MPESA_CALLBACK_URL
        password_bytes = (business_shortcode + lnm_passkey + timestamp).encode('ascii')
        password = base64.b64encode(password_bytes).decode('ascii')
        transaction_type = "CustomerPayBillOnline"

        payload = {
            "BusinessShortCode": business_shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": transaction_type,
            "Amount": self.amount,
            "PartyA": self.customer_number,
            "PartyB": business_shortcode,
            "PhoneNumber": self.customer_number,
            "CallBackURL": call_back_url,
            "AccountReference": self.customer_number,
            "TransactionDesc": self.transaction_desc ,
        }
        self.payload = payload

    def send_LNM_request(self):
        self.create_LNM_payload()
        token = cache.get("mpesa_auth_token")
        if not token:
            token = get_access_token()
        response = requests.post(settings.MPESA_LNM_URL, auth=BearerAuth(token), json=self.payload )
        data = json.loads(response.text)
        return data


@app.task(name="get_access_token")
def get_access_token():
    """Gets mpesa api token"""
    consumer_key = settings.MPESA_CONSUMER_KEY
    consumer_secret = settings.MPESA_CONSUMER_SECRET
    api_URL = settings.MPESA_GENERATE_AUTH_TOKEN_URL
    response = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    result = json.loads(response.text)
    cache.set("mpesa_auth_token", result["access_token"])
    return result["access_token"]


@app.task
def send_LNM_request(customer_number=None, amount=None, transaction_desc="test", company=None):
    """Wraps MpesaHandler send_LNM_request method"""
    mpesa_handler = MpesaHandler(customer_number=customer_number, amount=amount, transaction_desc=transaction_desc)
    result = mpesa_handler.send_LNM_request()
    
    payload = {}
    payload["company"] = company
    payload["checkout_request_id"] = result["CheckoutRequestID"]
    payload["response_code"] = result["ResponseCode"]
    payload["customer_number"] = customer_number
    RechargeRequest(**payload).save()
    return result
    

def validate_mpesa_callback_request(callback_transaction_time, recharge_request_time):
    """Validate time difference between recharge request and callback transaction time"""
    recharge_request_time = recharge_request_time.replace(tzinfo=None)
    time_difference = callback_transaction_time - recharge_request_time
    if time_difference > timedelta(seconds=60) or time_difference < timedelta(seconds=0):
        raise_validation_error({"detail": "Invalid request"}) 

def setup_get_mpesa_token_cron_job():
    crontab, _ = CrontabSchedule.objects.get_or_create(minute=59)
    periodic_task, _ = PeriodicTask.objects.get_or_create(
        crontab=crontab,
        name="get_access_token",
        task="core.utils.mpesa_helpers.get_access_token",
    )
