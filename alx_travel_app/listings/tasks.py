from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Booking

@shared_task
def send_payment_confirmation_email(booking_id):
    try:
        booking = Booking.objects.get(id=booking_id)
        subject = 'Payment Confirmation'
        message = f'Dear {booking.user.first_name}, your payment for booking\
         {booking.listing.title} has been successfully processed.'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [booking.user.email]
        
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        return f'Payment confirmation email sent to {booking.user.email}'
    except Booking.DoesNotExist:
        return f'Booking with id {booking_id} does not exist'
    except Exception as e:
        return f"Unexpected error: {str(e)}"


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 5, "countdown": 30},
    retry_backoff=True,
    retry_jitter=True,
)
def send_booking_confirmation_email(self, booking_id, recipient_email):
    """
    Sends booking confirmation email.
    Retries automatically on failure.
    """

    subject = "Booking Confirmation"
    message = f"Your booking (ID: {booking_id}) has been successfully created."

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [recipient_email],
        fail_silently=False,
    )