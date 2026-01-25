# services/payment_service.py
import logging
import time
import requests
from django.conf import settings
from django.shortcuts import get_object_or_404
from .models import Booking, Payment
from .tasks import send_payment_confirmation_email

# logger = logging.getLogger(__name__)

class PaymentService:
    
    @staticmethod
    def initiate_payment(booking_id: int):
        booking = get_object_or_404(Booking, id=booking_id)

        # Unique transaction reference
        tx_ref = f"booking-{booking.id}-{int(time.time())}"

        payload = {
            "amount": str(booking.listing.price_per_night),  # Chapa prefers strings for decimals
            "currency": "ETB",
            "email": booking.user.email,
            "first_name": booking.user.first_name,
            "last_name": booking.user.last_name,
            "tx_ref": tx_ref,
            "callback_url": "https://funniest-intently-doretta.ngrok-free.dev/api/payments/verify/",
        }

        headers = {
            "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(
                "https://api.chapa.co/v1/transaction/initialize",
                json=payload,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            # logger.error(f"Chapa connection error for booking {booking_id}: {str(e)}")
            return {"error": "Payment gateway connection failed"}, 502
        except ValueError:
            # logger.error(f"Invalid JSON response from Chapa for booking {booking_id}")
            return {"error": "Invalid response from payment gateway"}, 502

        if data.get("status") != "success":
            # logger.error(f"Chapa API returned an error for booking {booking_id}: {data}")
            return {"error": "Chapa API error", "details": data}, response.status_code

        # Create payment record in DB (idempotent: check if tx_ref exists)
        payment, created = Payment.objects.get_or_create(
            transaction_id=tx_ref,
            defaults={
                "booking": booking,
                "amount": payload["amount"],
                "status": "pending"
            }
        )

        return {"payment_url": data["data"]["checkout_url"]}, 200

    @staticmethod
    def verify_payment(tx_ref: str):
        if not tx_ref:
            return {"error": "Missing tx_ref"}, 400

        url = f"https://api.chapa.co/v1/transaction/verify/{tx_ref}"
        headers = {"Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"}

        try:
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            # logger.error(f"Chapa API request failed for tx_ref {tx_ref}: {e}")
            return {"error": "Failed to verify payment"}, 502
        except ValueError:
            # logger.error(f"Invalid JSON response from Chapa for tx_ref {tx_ref}")
            return {"error": "Invalid response from payment gateway"}, 502

        if data.get("status") != "success":
            return {"error": "Payment verification failed"}, 400

        try:
            payment = Payment.objects.select_related("booking").get(transaction_id=tx_ref)
        except Payment.DoesNotExist:
            # logger.warning(f"Payment not found for tx_ref {tx_ref}")
            return {"error": "Payment not found"}, 404

        # Idempotent update
        if payment.status != "completed":
            payment.status = "completed" if data["data"]["status"] == "success" else "failed"
            payment.save(update_fields=["status"])

            if payment.status == "completed":
                payment.booking.status = "confirmed"
                payment.booking.save(update_fields=["status"])
                send_payment_confirmation_email.delay(payment.booking.id)

        return {
            "payment_status": payment.status,
            "booking_status": payment.booking.status
        }, 200
