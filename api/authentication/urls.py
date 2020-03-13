from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from . import views

app_name = "auth"

urlpatterns = [
    path("login/", TokenObtainPairView.as_view(), name="get_token"),
    path("refresh/token/", TokenRefreshView.as_view(), name="refresh_token"),
    path("register/", views.RegistrationView.as_view(), name="registration"),
    path("add-staff/", views.AddStaffView.as_view(), name="add_staff"),
    path("companies/", views.GetCompaniesView.as_view(), name="get_companies"),
    path("companies/<int:pk>/", views.GetCompanyView.as_view(), name="get_company")
]
