from django.urls import path
from . import views

app_name = "sms"

urlpatterns = [
    path("", views.SMSRequestView.as_view(), name="sms"),
    path("template/", views.SMSTemplateView.as_view(), name="sms_template"),
    path("template/<int:pk>/", views.SingleSMSTemplateView.as_view(), name="single_sms_template"),
    path("groups/", views.GroupView.as_view(), name="group"),
    path("groups/<int:pk>/", views.SingleGroupView.as_view(), name="single_group"),
    path("groups/members/", views.GroupMembersView.as_view(), name="group_members"),
    path("group-members/<int:pk>/", views.SingleGroupMembersView.as_view(), name="single_group_member"),
    path("group-members/upload/", views.MassMemberUploadView.as_view(), name="mass-upload-member"),
    path("upload/", views.CsvSmsView.as_view(), name="csv_sms")
]
