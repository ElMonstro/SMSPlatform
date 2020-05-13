from django.db.utils import IntegrityError

from rest_framework import generics
from rest_framework.exceptions import ValidationError

from .utils.helpers import get_errored_integrity_field

class CustomCreateAPIView(generics.CreateAPIView):
    """
    This class adds the get_queryset function implementation that
    filter the queryset to only return user owned objects
    """

    def get_queryset(self):
        company = self.request.user.company
        queryset = super().get_queryset()
        return queryset.filter(company=company)

    def perform_create(self, serializer):
        # Catch unique together error 
        try: 
            serializer.save(company=self.request.user.company)
        except IntegrityError as error:
            field = get_errored_integrity_field(error)
            raise ValidationError({field: f'This {field} already exists'})


class CustomListAPIView(generics.ListAPIView):
    """
    This class adds the get_queryset function implementation that
    filter the queryset to only return user owned objects
    """

    def get_queryset(self):
        company = self.request.user.company
        queryset = super().get_queryset()
        return queryset.filter(company=company)


class CustomDestroyAPIView(generics.DestroyAPIView):
    """
    This class adds the get_queryset function implementation that
    filter the queryset to only return user owned objects
    """

    def get_queryset(self):
        company = self.request.user.company
        queryset = super().get_queryset()
        return queryset.filter(company=company)


class CustomUpdateAPIView(generics.UpdateAPIView):
    """
    This class adds the get_queryset function implementation that
    filter the queryset to only return user owned objects
    """

    def get_queryset(self):
        company = self.request.user.company
        queryset = super().get_queryset()
        return queryset.filter(company=company)
