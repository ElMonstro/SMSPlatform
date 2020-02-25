from django.db import IntegrityError
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from core.views import CustomCreateAPIView, CustomListAPIView
from . import serializers, models
from core.utils.helpers import raise_validation_error

class MpesaCallbackView(generics.CreateAPIView):
    """Mesa callback view"""
    serializer_class = serializers.PaymentSerializer
    queryset = models.Payment.objects.all()
    permission_classes = []

class PaymentListView(CustomListAPIView):
    """Enables Mpesa payment for sms recharge"""
    serializer_class = serializers.PaymentSerializer
    queryset = models.Payment.objects.all()

class RechargeView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = serializers.RechargeSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.send_request()
        status_code = status.HTTP_201_CREATED
        data = {
            "message": "Success, request accepted for processing"
        }
        return Response(data, status=status_code)

class CreateListRechargePlanView(generics.ListCreateAPIView):
    serializer_class = serializers.RechargePlanSerializer
    queryset = models.RechargePlan.objects.all()
