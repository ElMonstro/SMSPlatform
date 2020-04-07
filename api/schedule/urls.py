from django.urls import path
from . import views

urlpatterns = [
    path("", views.CreateScheduleView.as_view(), name="create_schedule"),
    path("<int:pk>/", views.RetrieveUpdateScheduleView.as_view(), name="single_schedule")
]
