from jwt import encode, decode

from django.core.mail import send_mail
from django.conf import settings

from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from . import serializers
from .models import AddStaffModel, Company
from core.permissions import IsAdmin, IsDirector, IsCompanyOwned, IsSuperUser, IsReseller


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
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self,request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        data = response.data.copy()
        data["message"] = "Success, registration email sent"
        return Response(data=data, status=status.HTTP_201_CREATED)


class GetCompanyView(generics.RetrieveAPIView):
    """Get Company data"""
    permission_classes = [IsAuthenticated, IsCompanyOwned]

    serializer_class = serializers.CompanySerializer
    queryset = Company.objects.all()


class GetCompaniesView(generics.ListAPIView):
    """Get all companies"""

    permission_classes = [IsAuthenticated, IsSuperUser]

    serializer_class = serializers.CompanySerializer
    queryset = Company.objects.all()


class InviteClient(APIView):
    
    permission_classes = [IsAuthenticated, IsReseller]

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
        