import os
import africastalking

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
