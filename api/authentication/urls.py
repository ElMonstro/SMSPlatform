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
    path("invite-client/", views.InviteClient.as_view(), name="invite_client"),
    path("companies/", views.GetCompaniesView.as_view(), name="get_companies"),
    path("companies/<int:pk>/", views.GetCompanyView.as_view(), name="get_company"),
    path("verify-user/", views.VerifyUser.as_view(), name="verify_user"),
    path("reset-password/send-email/", views.SendPasswordResetEmail.as_view(), name="send_reset_email"),
    path("reset-password/", views.ResetPassword.as_view(), name="reset_password"),
    path("consumer-keys/", views.CreateConsumerKeyView.as_view(), name="create_consumer_key"),
    path("consumer-keys/<int:pk>/", views.DeleteConsumerKeyView.as_view(), name="delete_consumer_key"),
    path("consumer-keys/activity/", views.GetKeyActivityKeyView.as_view(), name="get_key_activity"),
    path("consumer-keys/<int:pk>/activity/", views.GetSingleKeyActivityKeyView.as_view(), name="get_single_key_activity"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("public-key/", views.GetPublicKey.as_view(), name="public-key")
]
