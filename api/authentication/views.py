from rest_framework.response import Response
from rest_framework import status, generics

from . import serializers
from .models import AddStaffModel, Company
from core.permissions import IsAdmin


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
        ] = "Account created successfully. Please confirm from your email."
        if self.request.query_params.get("user") == "staff":
            payload["message"] =  "Account created successfully. Go ahead and login"
            
        return Response(payload, status=status.HTTP_201_CREATED)


class AddStaffView(generics.CreateAPIView):
    """Add emails for staff members registration"""
    
    serializer_class = serializers.AddStaffSerializer
    queryset = AddStaffModel.objects.all()
    permission_classes = [IsAdmin]

    def post(self,request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        data = response.data.copy()
        data["message"] = "Success, registration email sent"
        return Response(data=data, status=status.HTTP_201_CREATED)


class GetCompanyView(generics.RetrieveAPIView):
    """Get Company data"""
    serializer_class = serializers.CompanySerializer
    queryset = Company.objects.all()


class GetCompaniesView(generics.ListAPIView):
    """Get all companies"""
    serializer_class = serializers.CompanySerializer
    queryset = Company.objects.all()

