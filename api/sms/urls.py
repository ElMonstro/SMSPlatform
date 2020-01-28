from django.urls import path
from . import views

app_name = "sms"

urlpatterns = [
    path("", views.SMSRequestView.as_view(), name="sms"),
    path("template/", views.SMSTemplateView.as_view(), name="sms_template"),
    path("template/<int:pk>/", views.SingleSMSTemplateView.as_view()),
]
