from django.db import IntegrityError
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from core.views import CustomCreateAPIView, CustomListAPIView
from . import serializers, models
from core.utils.helpers import raise_validation_error
from core.views import CustomCreateAPIView, CustomListAPIView
from core.permissions import IsSuperUser, IsReseller

class MpesaCallbackView(generics.CreateAPIView):
    """Mesa callback view"""
    serializer_class = serializers.PaymentSerializer
    queryset = models.Payment.objects.all()
    permission_classes = []

class PaymentListView(generics.CreateAPIView, CustomListAPIView):
    """Enables Mpesa payment for sms recharge"""
    serializer_class = serializers.PaymentSerializer
    queryset = models.Payment.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        message = serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({ 'message': message }, status=status.HTTP_201_CREATED, headers=headers)




class MpesaPayView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = serializers.MpesaPaySerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.send_request()
        status_code = status.HTTP_201_CREATED
        data = {
            "message": "Success, request accepted for processing"
        }
        return Response(data, status=status_code)

class CreatRechargePlanView(generics.CreateAPIView):

    permission_classes = [IsAuthenticated, IsSuperUser]
    
    serializer_class = serializers.RechargePlanSerializer
    queryset = models.RechargePlan.objects.all()


class ListRechargePlanView(generics.ListCreateAPIView):

    permission_classes = [IsAuthenticated]
    
    serializer_class = serializers.RechargePlanSerializer
    queryset = models.RechargePlan.objects.all()


class DeleteUpdateRechargePlanView(generics.RetrieveUpdateDestroyAPIView):

    permission_classes = [IsAuthenticated, IsSuperUser]
    
    serializer_class = serializers.RechargePlanSerializer
    queryset = models.RechargePlan.objects.all()

class SetBrandingFeeView(generics.ListCreateAPIView):
    """Set Branding Fee"""
    permission_classes = [IsAuthenticated, IsSuperUser]
    serializer_class = serializers.BrandingFeeSerializer
    queryset = models.BrandingFee.objects.all()

    def post(self, request, *args, **kwargs):
        if self.get_queryset():
            return Response({"detail": "Fee already created, you have to edit the current fee"}, status.HTTP_400_BAD_REQUEST)
        return super().post(request, *args, **kwargs)


class EditBrandingFeeView(generics.RetrieveUpdateAPIView):
    """Edit Branding Fee """   
    permission_classes = [IsAuthenticated, IsSuperUser]
    serializer_class = serializers.BrandingFeeSerializer
    queryset = models.BrandingFee.objects.all()
