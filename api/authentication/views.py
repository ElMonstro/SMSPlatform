from rest_framework.response import Response
from rest_framework import status, generics

from .serializers import RegistrationSerializer


class RegistrationView(generics.CreateAPIView):

    serializer_class = RegistrationSerializer
    permission_classes = []

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        payload = response.data.copy()
        payload[
            "message"
        ] = "Account created successfully. Please confirm from your email."

        return Response(payload, status=status.HTTP_201_CREATED)
