import os
from math import ceil
from decimal import Decimal
from rest_framework.exceptions import ValidationError
import africastalking

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from jamboSms.celery import app

from api.authentication.models import Company
from api.sms.models import SentSMS
from .helpers import camel_to_snake

username = os.getenv("AIT_USERNAME")
api_key = os.getenv("AIT_API_KEY")
africastalking.initialize(username, api_key)
sms = africastalking.SMS

def company_is_branded(company):
    """
    Check if user has requested branding
    params:
        company - Company object
    returns: Boolean
    """
    try:
        company.brand
    except ObjectDoesNotExist:
        return False
    return True

def get_sms_branding(company_id):
    """
    Get SMS branding name is avilable and approved
    params:
        company - Company object
    returns: String
    """
    brand_name = settings.COMPANY_BRAND_NAME
    
    if not company_id:
        return brand_name

    company = Company.objects.get(pk=company_id)
    if not company_is_branded(company):
        return brand_name

    brand_object = company.brand

    if brand_object.is_active and brand_object.is_approved:
        brand_name = brand_object.name
    return brand_name

def log_sent_message(recipient, company):
    recipient = {camel_to_snake(k):v for (k,v) in recipient.items()}
    recipient.pop("cost")
    recipient.pop("number")
    SentSMS.objects.create(company=company, **recipient)

@app.task(name="send_sms")
def send_sms(message, number_list, company_id=None):
    """
    sends an SMS to a list of phone numbers
    params:
        message - string
        number_list - list of strings
    returns: response from AIT api
    """

    sender_id = None

    
    brand_name = get_sms_branding(company_id)
    sender_id = brand_name

    response_data = sms.send(message, number_list, sender_id)

    if company_id:
        company = Company.objects.get(pk=company_id)
        recipients = response_data["SMSMessageData"]["Recipients"]
        for recipient in recipients:
            log_sent_message(recipient, company)        
    

def create_personalized_message(greeting_text, first_name, message):
    return greeting_text + ' ' + first_name + ', ' + message

@app.task(name="send_mass_unique_sms")
def send_mass_unique_sms(message, greeting_text, contact_list, company_id):
    """Loop through contacts and send unique sms"""
    sender_id = get_sms_branding(company_id)
    company = Company.objects.get(pk=company_id)

    for contact in contact_list:
        first_name = contact["first_name"]
        number = contact["phone"]
        personalized_message = create_personalized_message(greeting_text, first_name, message)
        response_data = sms.send(personalized_message, [number], sender_id)
        recipients = response_data["SMSMessageData"]["Recipients"]
        log_sent_message(recipients[0], company)  

def get_number_of_sms_for_message(message):
    """Gets the number of sms needed to send passed message"""
    return ceil(len(message) / 160)

def count_sms(message, recepients):
    """Count same sms for a number of receipients"""
    sms_count = get_number_of_sms_for_message(message) * len(recepients)
    return sms_count

def count_personalized_sms(message, greeting_text, contact_list):
    total_sms = 0
    for contact in contact_list:
        personalized_message = create_personalized_message(greeting_text, contact["first_name"], message)
        sms_count_for_message = get_number_of_sms_for_message(personalized_message)
        total_sms += sms_count_for_message
    return total_sms

def update_sms_count(sms_count, company, add=False):
    if add:
        company.sms_count += sms_count
    else:
        if sms_count > company.sms_count:
            raise ValidationError({"detail": f"You do not have enough SMS balance to send this messages, please top up. Your balance is {company.sms_count}"})
        company.sms_count -= sms_count
    company.save()
    return company.sms_count

def update_email_count(email_count, company, add=False):
    """
    Update email count
    """
    if add:
        company.email_count += email_count
    else:
        if email_count > company.email_count:
            raise ValidationError({"detail": f"You do not have enough emails balance to send this messages, please top up. Your balance is {company.email_count}"})
        company.email_count -= email_count
    company.save()
    return company.email_count


def calculate_recharge_sms(queryset, amount):
    """
    Choose a price rate from the database and calculate sms recharge
    """
    queryset = queryset.order_by("price_limit")
    rate = None
    for recharge_plan in queryset:
        if  amount <= recharge_plan.price_limit:
            rate = recharge_plan.rate
            break
    if not rate:
        rate = list(queryset)[-1].rate
    sms_count = Decimal(amount) // rate
    return sms_count
