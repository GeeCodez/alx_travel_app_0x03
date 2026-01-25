from django.core.management.base import BaseCommand
from django.db import transaction
from listings.models import Listing, Booking, Review
from django.contrib.auth.models import User
from django.utils import timezone
from faker import Faker
import random

fake = Faker()

class Command(BaseCommand):
    help = 'Seed the database with sample users, listings, bookings, and reviews'

    def handle(self, *args, **kwargs):
        try:
            with transaction.atomic():
                self.create_users()
                self.create_listings()
                self.create_bookings()
                self.create_reviews()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Seeding failed: {e}'))
            # Transaction automatically rolls back
        else:
            self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))
    # -------------------
    # USERS
    # -------------------
    def create_users(self):
        self.users = []
        for _ in range(10):
            username = fake.user_name()
            user, created = User.objects.get_or_create(username=username)
            if created:
                user.set_password('password123')
                user.save()
            self.users.append(user)
        self.stdout.write(f'Created {len(self.users)} users')

    # -------------------
    # LISTINGS
    # -------------------
    def create_listings(self):
        self.listings = []
        for _ in range(15):
            owner = random.choice(self.users)
            listing = Listing.objects.create(
                owner=owner,
                title=fake.sentence(nb_words=4),
                description=fake.paragraph(nb_sentences=3),
                location=fake.city(),
                price_per_night=round(random.uniform(50, 500), 2),
                max_guests=random.randint(1, 6)
            )
            self.listings.append(listing)
        self.stdout.write(f'Created {len(self.listings)} listings')

    # -------------------
    # BOOKINGS
    # -------------------
    def create_bookings(self):
        self.bookings = []
        for _ in range(30):
            user = random.choice(self.users)
            listing = random.choice(self.listings)
            check_in = fake.date_between(start_date='-60d', end_date='today')
            check_out = fake.date_between(start_date=check_in, end_date='+10d')
            booking = Booking.objects.create(
                user=user,
                listing=listing,
                check_in=check_in,
                check_out=check_out,
                guests=random.randint(1, listing.max_guests),
                status=random.choice(['pending', 'confirmed', 'cancelled', 'completed'])
            )
            self.bookings.append(booking)
        self.stdout.write(f'Created {len(self.bookings)} bookings')

    # -------------------
    # REVIEWS
    # -------------------
    def create_reviews(self):
        count = 0
        for booking in self.bookings:
            # Only completed bookings can have reviews
            if booking.status == 'completed':
                review = Review.objects.create(
                    user=booking.user,
                    listing=booking.listing,
                    rating=random.randint(1, 5),
                    comment=fake.paragraph(nb_sentences=2),
                    created_at=fake.date_time_between(start_date=booking.check_in, end_date=timezone.now())
                )
                count += 1
        self.stdout.write(f'Created {count} reviews')
