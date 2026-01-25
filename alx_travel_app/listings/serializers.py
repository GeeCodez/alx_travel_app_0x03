from rest_framework import serializers
from .models import Listing, Booking

# -------------------
# Listing Serializer
# -------------------
class ListingSerializer(serializers.ModelSerializer):
    owner_username = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Listing
        fields = [
            'id',
            'owner',
            'owner_username',
            'title',
            'description',
            'location',
            'price_per_night',
            'max_guests',
            'created_at',
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'owner_username']

# -------------------
# Booking Serializer
# -------------------
class BookingSerializer(serializers.ModelSerializer):
    user_username = serializers.ReadOnlyField(source='user.username')
    listing_title = serializers.ReadOnlyField(source='listing.title')

    class Meta:
        model = Booking
        fields = [
            'id',
            'user',
            'user_username',
            'listing',
            'listing_title',
            'check_in',
            'check_out',
            'guests',
            'status',
            'created_at',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'user_username', 'listing_title']

    # -------------------
    # Example validation: check_in < check_out
    # -------------------
    def validate(self, data):
        if data['check_in'] >= data['check_out']:
            raise serializers.ValidationError("check_in date must be before check_out date")
        return data
