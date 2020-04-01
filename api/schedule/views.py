from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response

from django_celery_beat.models import PeriodicTask

from . import serializers, models


class CreateScheduleView(generics.GenericAPIView):
    """Register SMS schedule"""
    serializer_class = serializers.PeriodicTaskSerializer
    queryset = models.ScheduleRegistry.objects.all()
    
    def post(self, request, *args, **kwargs):
        serializer = serializers.CrontabScehduleSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        period_task_instance = serializer.save()
        period_task_serializer  = serializers.PeriodicTaskSerializer(instance=period_task_instance)
        return Response(data=period_task_serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        schedule_registry, _ = models.ScheduleRegistry.objects.get_or_create(company=request.user.company)
        schedules = schedule_registry.schedules.all()
        serializer = serializers.PeriodicTaskSerializer(schedules, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class RetrieveUpdateScheduleView(generics.RetrieveUpdateDestroyAPIView):
    """Delete, update and delete scheduled sms send tasks"""

    serializer_class = serializers.PeriodicTaskSerializer
    
    def get_queryset(self):
        company = self.request.user.company
        instance = models.ScheduleRegistry.objects.get(company=company)
        return instance.schedules.all()

    def get_serializer_class(self):
        serializer_class = super().get_serializer_class()
        if self.request.query_params.get("update") == "time":
            serializer_class = serializers.UpdateScheduleTimeSerializer
        return serializer_class

    def update(self, request, *args, **kwargs):
        
        response = super().update(request, *args, **kwargs)
        
        if self.request.query_params.get("update") == "time":  
            pk = kwargs['pk']
            instance = models.PeriodicTask.objects.get(pk=pk)
            serializer = serializers.PeriodicTaskSerializer(instance)
            response = Response(serializer.data)
        
        return response
        
