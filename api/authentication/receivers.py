from django.dispatch import receiver
from core.signals import api_key_approved

from core.utils.helpers import log

@receiver(api_key_approved)
def send_mail_on_publish(sender, **kwargs):
    log("stuff")
    print("stuff")
