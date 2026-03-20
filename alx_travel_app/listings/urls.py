from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ListingViewSet, BookingViewSet, api_root
from . import views

router = DefaultRouter()
router.register(r'listings', ListingViewSet, basename='listing')
router.register(r'bookings', BookingViewSet, basename='booking')

urlpatterns = [
    path('', api_root, name='api-root'),

    path("payments/initiate/<int:booking_id>/", views.initiate_payment, name="initiate_payment"),
    path("payments/verify/", views.verify_payment, name="verify_payment"),
]

urlpatterns += router.urls