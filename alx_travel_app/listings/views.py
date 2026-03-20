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
class ListingViewSet(viewsets.ModelViewSet):
    permission_classes=[]
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
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