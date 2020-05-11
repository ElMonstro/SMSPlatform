from django.dispatch import Signal
api_key_approved = Signal(providing_args=["url", "method"])