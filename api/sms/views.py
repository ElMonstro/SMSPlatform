from django.db import IntegrityError

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError

from . import serializers, models
from core.utils.sms_helpers import send_sms
from core.permissions import IsCompanyOwned
from core.views import CustomCreateAPIView
from core.utils.helpers import CsvExcelReader, get_errored_integrity_field



class ModelSerializerMappingMixin:


    def map_serializer_to_view(self, medium, view):
        """Get serializer for passed view and medium"""
        view_serializer_mapping = {
            'group': {
                None: serializers.SMSGroupSerializer,
                "email": serializers.EmailGroupSerializer
                },
            'member': {
                None: serializers.GroupMemberSerializer,
                "email": serializers.EmailGroupMemberSerializer
                },
            'request': {
                None: serializers.SMSRequestSerializer,
                "email": serializers.EmailRequestSerializer
            }
        }
        return view_serializer_mapping[view][medium]


    def map_queryset_to_view(self, medium, view):
        """Get queryset for passed view and medium"""
        view_model_mapping = {
            'group': {
                None: models.SMSGroup,
                "email": models.EmailGroup
                },
            'member': {
                None: models.GroupMember,
                "email": models.EmailGroupMember
            },
            'request': {
                None: models.SMSRequest,
                "email": models.EmailRequest
            }
        }
        company = self.request.user.company
        return view_model_mapping[view][medium].objects.filter(company=company)

    


class SMSRequestView(generics.ListAPIView, CustomCreateAPIView, ModelSerializerMappingMixin):
    """create, list and delete sms requests """

    def get_serializer_class(self):
        medium = self.request.query_params.get("medium", None)
        return self.map_serializer_to_view(medium, "request")

    def get_queryset(self):
        medium = self.request.query_params.get("medium", None)
        return self.map_queryset_to_view(medium, "request")

    def delete(self, request):
        serializer = serializers.DeleteSMSRequestsSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SMSTemplateView(generics.ListAPIView, CustomCreateAPIView):
    """Create or list sms templates"""

    serializer_class = serializers.SMSTemplateSerializer
    queryset = models.SMSTemplate.objects.all()


class SingleSMSTemplateView(generics.RetrieveUpdateDestroyAPIView, CustomCreateAPIView):
    """Single SMS actions"""

    permission_classes = [IsAuthenticated, IsCompanyOwned]
    serializer_class = serializers.SMSTemplateSerializer
    queryset = models.SMSTemplate.objects.all()

class GroupView(generics.ListAPIView, ModelSerializerMappingMixin, CustomCreateAPIView):
    """Create or list groups"""

    queryset = models.SMSGroup.objects.all()
    serializer_class = serializers.SMSGroupSerializer
    
    def perform_create(self, serializer):
        # Catch unique together error 
        try: 
            serializer.save(company=self.request.user.company)
        except IntegrityError as error:
            field = get_errored_integrity_field(error)
            raise ValidationError({field: f'This {field} already exists'})

    def get_serializer_class(self):
        medium = self.request.query_params.get("medium", None)
        return self.map_serializer_to_view(medium, "group")

    def get_queryset(self):
        medium = self.request.query_params.get("medium", None)
        return self.map_queryset_to_view(medium, "group")



class SingleGroupView(generics.RetrieveUpdateDestroyAPIView, ModelSerializerMappingMixin):
    """
    Get, delete and update a group, Patch update is used to add members while PUT 
    update is used to remove members
    """

    permission_classes = [IsAuthenticated, IsCompanyOwned]

    def get_serializer_class(self):
        medium = self.request.query_params.get("medium", None)
        if medium == "email":
            return serializers.SingleEmailGroupSerializer
        return serializers.SingleSMSGroupSerializer

    def get_queryset(self):
        medium = self.request.query_params.get("medium", None)
        return self.map_queryset_to_view(medium, "group")


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
            group_member_action[self.request.method](*new_members)
            serializer.instance.save()
        serializer.save()


class GroupMembersView(generics.ListAPIView,CustomCreateAPIView, ModelSerializerMappingMixin):
    """Create or list members"""
    def get_serializer_class(self):
        medium = self.request.query_params.get("medium", None)
        return self.map_serializer_to_view(medium, "member")

    def get_queryset(self):
        medium = self.request.query_params.get("medium")
        return self.map_queryset_to_view(medium, "member")



class SingleGroupMembersView(generics.RetrieveUpdateDestroyAPIView, ModelSerializerMappingMixin):
    """Update, delete and get actions on members"""

    def get_serializer_class(self):
        medium = self.request.query_params.get("medium", None)
        return self.map_serializer_to_view(medium, "member")

    def get_queryset(self):
        medium = self.request.query_params.get("medium", None)
        return self.map_queryset_to_view(medium, "member")


class MassMemberUploadView(generics.GenericAPIView):
    """Upload members through csv or excel file"""
    serializer_class = serializers.CsvMembersUploadSerializer
    queryset = models.GroupMember.active_objects.all()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data, status.HTTP_201_CREATED)

class CsvSmsView(generics.GenericAPIView):
    """Send sms to contacts on csv or excel file"""
    serializer_class = serializers.CsvSmsContactUpload
    queryset = models.GroupMember.active_objects.all()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if self.request.query_params.get("sms") == "personalized":
            data = serializer.send_personalized_sms()
        elif self.request.query_params.get("medium") == "email":
            data = serializer.send_email() 
        else:
            data = serializer.send_sms()
        return Response(data, status.HTTP_201_CREATED)
        