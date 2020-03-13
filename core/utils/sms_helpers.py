import os
from math import ceil
from decimal import Decimal
from rest_framework.exceptions import ValidationError
import africastalking
from jamboSms.celery import app

username = os.getenv("AIT_USERNAME")
api_key = os.getenv("AIT_API_KEY")
africastalking.initialize(username, api_key)
sms = africastalking.SMS

@app.task(name="send_sms")
def send_sms(message, number_list):
    """
    sends an SMS to a list of phone numbers
    params:
        message - string
        number_list - list of strings
    returns: response from AIT api
    """
    return sms.send(message, number_list)

def create_personalized_message(greeting_text, first_name, message):
    return greeting_text + ' ' + first_name + ', ' + message

@app.task(name="send_mass_unique_sms")
def send_mass_unique_sms(message, greeting_text, contact_list):
    """Loop through contacts and send unique sms"""
    for contact in contact_list:
        first_name = contact["first_name"]
        number = contact["phone"]
        personalized_message = create_personalized_message(greeting_text, first_name, message)
        send_sms(personalized_message, [number])

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
            raise ValidationError({"detail": "You do not have enough SMS remaining to send this messages, please top up"})
        company.sms_count -= sms_count
    company.save()
    return company.sms_count


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
    