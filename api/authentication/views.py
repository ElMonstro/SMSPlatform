from jwt import encode, decode

from django.core.mail import send_mail
from django.conf import settings

from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from . import serializers
from .models import (AddStaffModel, Company, ResetPasswordToken,
 ConsumerKey, APIKeyActivity, User)
from core.permissions import (IsAdmin, IsDirector, IsCompanyOwned,
 IsSuperUser, IsReseller, IsVerified)
from core.views import CustomCreateAPIView, CustomDestroyAPIView, CustomListAPIView


class RegistrationView(generics.CreateAPIView):

    serializer_class = serializers.RegistrationSerializer
    permission_classes = []

    def get_serializer_class(self):
        if self.request.query_params.get("user") == "staff":
            serializer =  serializers.StaffRegistrationSerializer
        elif  self.request.query_params.get("user") == "reseller":
            serializer = serializers.ResellerRegistration
        elif  self.request.query_params.get("parent_company"):
            serializer = serializers.ResellerClientSerializer
        else: 
            serializer = super().get_serializer_class()
        return serializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        payload = response.data.copy()
        payload[
            "message"
        ] = "Account created successfully. Please verify from your email."
        if self.request.query_params.get("user") == "staff":
            payload["message"] =  "Account created successfully. Go ahead and login"
            
        return Response(payload, status=status.HTTP_201_CREATED)


class AddStaffView(generics.CreateAPIView):
    """Add emails for staff members registration"""
    
    serializer_class = serializers.AddStaffSerializer
    queryset = AddStaffModel.objects.all()
    permission_classes = [IsAuthenticated, IsAdmin, IsVerified]

    def post(self,request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        data = response.data.copy()
        data["message"] = "Success, registration email sent"
        return Response(data=data, status=status.HTTP_201_CREATED)


class GetCompanyView(generics.RetrieveAPIView):
    """Get Company data"""
    permission_classes = [IsAuthenticated, IsCompanyOwned, IsVerified]

    serializer_class = serializers.CompanySerializer
    queryset = Company.objects.all()


class GetCompaniesView(generics.ListAPIView):
    """Get all companies"""

    permission_classes = [IsAuthenticated, IsSuperUser]

    serializer_class = serializers.CompanySerializer
    queryset = Company.objects.all()


class InviteClient(APIView):
    
    permission_classes = [IsAuthenticated, IsReseller, IsVerified]

    def post(self, request, *args, **kwargs):
        serializer = serializers.InviteClientSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        company_name = request.user.company.name
        subject = f"{company_name} registration link"
        message = f"Click this link to register to {company_name}: {settings.FRONTEND_LINK}resellers/{company_name}"
        send_mail(subject, message, company_name, [email])
        return Response({"message": f"Success, invitation link sent to client email ({email})"})


class VerifyUser(APIView):

    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = serializers.VerifyUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"detail": "Success, user verified"})


class SendPasswordResetEmail(APIView):

    permission_classes = []
    serializer_class = serializers.PasswordResetSerializer
    queryset = ResetPasswordToken.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = serializers.PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.is_user_available():
            serializer.save()
        return Response({"detail": "Success, user reset link sent"})
        

class ResetPassword(APIView):

    permission_classes = []

    def patch(self, request, *args, **kwargs):
        serializer = serializers.UpdatePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.update_password()
        return Response({"detail": "Success, password reset"})


class CreateConsumerKeyView(generics.ListAPIView, CustomCreateAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = serializers.CreateConsumerKeySerializer
    queryset = ConsumerKey.objects.all()

    def post(self, request, *args, **kwargs):
        if len(self.get_queryset()) > 4:
            return Response({"detail": "Maximum number of api keys allowed is 5"}, status.HTTP_400_BAD_REQUEST)
        return super().post(request, *args, **kwargs)


class DeleteConsumerKeyView(CustomDestroyAPIView):
    
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.CreateConsumerKeySerializer
    queryset = ConsumerKey.objects.all()

    def perform_destroy(self, instance):
        instance.user.delete()
        instance.delete()


class GetKeyActivityKeyView(generics.ListAPIView):

    permission_classes = [IsAuthenticated,]
    serializer_class = serializers.KeyActivitySerializer
    queryset = APIKeyActivity.objects.all()


class GetSingleKeyActivityKeyView(generics.ListAPIView):

    permission_classes = [IsAuthenticated,]
    serializer_class = serializers.KeyActivitySerializer
    queryset = ConsumerKey.objects.all()

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        queryset = instance.activity.all()
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class ProfileView(APIView):
    """Get profile"""
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        instance = request.user
        serializer = serializers.ProfileSerializer(instance)
        return Response(serializer.data)

