from django.urls import path
from . import views

urlpatterns = [
    path("sms/", views.CreateScheduleView.as_view(), name="create_sms_schedule"),
    path("sms/<int:pk>/", views.RetrieveUpdateScheduleView.as_view(), name="single_schedule")
]
