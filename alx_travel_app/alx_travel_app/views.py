from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import permissions

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def home(request, format=None):
    return Response({
        "message": "Welcome to ALX Travel App API 🚀",
        "api_root": reverse('api-root', request=request, format=format),
        "swagger_docs": request.build_absolute_uri('/swagger/'),
        "admin": request.build_absolute_uri('/admin/'),
        "authentication": {
            "login": reverse('token_obtain_pair', request=request, format=format),
            "refresh": reverse('token_refresh', request=request, format=format),
        },
        "endpoints": {
            "listings": reverse('listing-list', request=request),
            "bookings": reverse('booking-list', request=request),
        }
    })