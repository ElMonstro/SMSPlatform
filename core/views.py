from rest_framework.generics import GenericAPIView


class CustomGenericAPIView(GenericAPIView):
    """
    This class adds the get_queryset function implementation that
    filter the queryset to only return the request user owned objects
    """

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        return queryset.filter(owner=user)

