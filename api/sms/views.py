from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from . import serializers, models
from core.utils.sms_helpers import send_sms
from core.permissions import IsOwnerorSuperuser, IsOwner
from core.views import CustomGenericAPIView


class SMSRequestView(generics.ListCreateAPIView, CustomGenericAPIView):
    """create, list and delete sms requests """

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

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
class SingleSMSTemplateView(generics.RetrieveUpdateDestroyAPIView, CustomGenericAPIView):
    """Single SMS actions"""

    permission_classes = [IsOwner]
    serializer_class = serializers.SMSTemplateSerializer
    queryset = models.SMSTemplate.objects.all()

class GroupView(generics.ListCreateAPIView, CustomGenericAPIView):
    """Create or list groups"""
    serializer_class = serializers.SMSGroupSerializer
    queryset = models.SMSGroup.objects.all()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class SingleGroupView(generics.RetrieveUpdateDestroyAPIView, CustomGenericAPIView):
    """
    Get, delete and update a group, Patch update is used to add members while PUT 
    update is used to remove members
    """

    permission_classes = [IsOwner]
    serializer_class = serializers.SingleSMSGroupSerializer
    queryset = models.SMSGroup.objects.all()

    def perform_update(self, serializer):
        """
        Change members m2m field update behaviour 
        to add or remove existing members instead of replacing
        """
        new_members = serializer.validated_data.pop("members", None)
        group_member_action = {
            "PATCH": serializer.instance.members.add,
            "PUT": serializer.instance.members.remove
        }
        if new_members:
            for new_member in new_members:
                group_member_action[self.request.method](new_member)
            serializer.instance.save()
        serializer.save()


class GroupMembersView(generics.CreateAPIView, CustomGenericAPIView):
    """Create or list members"""
    serializer_class = serializers.GroupMemberSerializer
    queryset = models.GroupMember.active_objects.all()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class SingleGroupMembersView(generics.RetrieveUpdateDestroyAPIView):
    """Update, delete and get actions on members"""
    serializer_class = serializers.GroupMemberSerializer
    queryset = models.GroupMember.active_objects.all()
