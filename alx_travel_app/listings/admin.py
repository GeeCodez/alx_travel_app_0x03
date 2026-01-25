from django.contrib import admin
from .models import Listing, Booking, Review, Payment

admin.site.register(Listing)
admin.site.register(Booking)
admin.site.register(Review)
admin.site.register(Payment)
