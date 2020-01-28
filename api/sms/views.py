from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from . import serializers, models
from core.utils.sms_helpers import send_sms
from core.permissions import IsOwnerorSuperuser, IsOwner
from core.views import CustomGenericAPIView


class SMSRequestView(generics.ListCreateAPIView, CustomGenericAPIView):
    """Send sms view """

    serializer_class = serializers.SMSRequestSerializer
    queryset = models.SMSRequest.active_objects.all()

    def delete(self, request):
        serializer = serializers.DeleteSMSRequestsSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid()
        serializer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class SMSTemplateView(generics.ListCreateAPIView, CustomGenericAPIView):
    """Create or list sms templates"""

    serializer_class = serializers.SMSTemplateSerializer
    queryset = models.SMSTemplate.objects.all()


class SingleSMSTemplateView(generics.RetrieveUpdateDestroyAPIView):
    """Single SMS actions"""

    permission_classes = [IsOwner]
    serializer_class = serializers.SMSTemplateSerializer
    queryset = models.SMSTemplate.objects.all()
