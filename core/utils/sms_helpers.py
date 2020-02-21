import os
import africastalking
from jamboSms.celery import app

username = os.getenv("AIT_USERNAME")
api_key = os.getenv("AIT_API_KEY")
africastalking.initialize(username, api_key)
sms = africastalking.SMS


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
