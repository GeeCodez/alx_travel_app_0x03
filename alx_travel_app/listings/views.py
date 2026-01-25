from rest_framework import viewsets, permissions
from .models import Listing, Booking, Payment
from .serializers import ListingSerializer, BookingSerializer
from .services import PaymentService
import requests
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.db import transaction

from .tasks import send_booking_confirmation_email,send_payment_confirmation_email

def initiate_payment(request, booking_id):
    result, status = PaymentService.initiate_payment(booking_id)
    return JsonResponse(result, status=status)

def verify_payment(request):
    tx_ref = request.GET.get("trx_ref")
    result, status = PaymentService.verify_payment(tx_ref)
    return JsonResponse(result, status=status)
# --------------------
# Listing ViewSet
# --------------------
class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        # Automatically set the owner to the current user
        serializer.save(owner=self.request.user)

# --------------------
# Booking ViewSet
# --------------------
class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Automatically set the user to the current user
        booking=serializer.save(user=self.request.user)

        recipient_email = booking.user.email
        booking_id = booking.id

        # Trigger task ONLY after DB commit
        transaction.on_commit(
            lambda: send_booking_confirmation_email.delay(
                booking_id=booking_id,
                recipient_email=recipient_email,
            )
        )