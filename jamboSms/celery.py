from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jamboSms.settings')
app = Celery('jamboSms')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    from core.utils.mpesa_helpers import get_access_token
    # Calls every 10 seconds.
    sender.add_periodic_task(3590.0, get_access_token.s(), name='create token every hour')

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
