from rest_framework import viewsets, permissions
from .models import Listing, Booking, Payment
from .serializers import ListingSerializer, BookingSerializer
from .services import PaymentService
from django.conf import settings
from django.http import JsonResponse
from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.reverse import reverse
from .tasks import send_booking_confirmation_email,send_payment_confirmation_email


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def api_root(request, format=None):
    return Response({
        'listings': reverse('listing-list', request=request, format=format),
        'bookings': reverse('booking-list', request=request, format=format),
        # 'initiate_payment': reverse('initiate_payment', request=request, format=format),
        # 'verify_payment': reverse('verify_payment', request=request, format=format),
        'login': reverse('token_obtain_pair', request=request, format=format),
    })

def initiate_payment(request, booking_id):
    result, status = PaymentService.initiate_payment(booking_id)
    return JsonResponse(result, status=status)

def verify_payment(request):
    tx_ref = request.GET.get("trx_ref")
    result, status = PaymentService.verify_payment(tx_ref)
    return JsonResponse(result, status=status)

class ListingViewSet(viewsets.ModelViewSet):
    permission_classes=[]
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Booking.objects.none()
        return Booking.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        booking=serializer.save(user=self.request.user)

        recipient_email = booking.user.email
        booking_id = booking.id

        transaction.on_commit(
            lambda: send_booking_confirmation_email.delay(
                booking_id=booking_id,
                recipient_email=recipient_email,
            )
        )