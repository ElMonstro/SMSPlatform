from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,

)
from .views import RegistrationView
app_name = 'auth'

urlpatterns =[
    path('login/', TokenObtainPairView.as_view(), name='get_token'),
    path('refresh/token/', TokenRefreshView.as_view(), name='refresh_token'),
    path('register/', RegistrationView.as_view(), name='registration')
]