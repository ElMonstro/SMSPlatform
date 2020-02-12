from django.db.utils import IntegrityError

from rest_framework import generics
from rest_framework.exceptions import ValidationError

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
            raise ValidationError({"detail": error})
