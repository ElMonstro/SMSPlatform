from django.urls import path, include

app_name = "api_v1"
urlpatterns = [
    path("auth/", include("api.authentication.urls")),
    path("messages/", include("api.sms.urls")),
    path("payments/", include("api.payment.urls")),
    path("schedules/", include("api.schedule.urls"))
]
