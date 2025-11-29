from django.db import models
from django.conf import settings
import boto3


class Room(models.Model):
    ROOM_TYPES = [
        ("classic", "Classic Room"),
        ("premium", "Premium Room"),
        ("studio", "Studio Apartment"),
    ]

    name = models.CharField(max_length=120)
    location = models.CharField(max_length=120)
    room_type = models.CharField(max_length=50, choices=ROOM_TYPES)
    price_per_night = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="rooms/", blank=True, null=True)
    s3_url = models.URLField(max_length=500, blank=True, null=True)
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.get_room_type_display()})"

    @property
    def signed_image_url(self):
        if not self.image:
            return ""

        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        region_name = getattr(settings, "AWS_S3_REGION_NAME", "us-east-1")

        s3_client = boto3.client("s3", region_name=region_name)

        return s3_client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": bucket_name,
                "Key": self.image.name,
            },
            ExpiresIn=3600,
        )


class Booking(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
    ]

    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name="bookings",
    )
    user_email = models.EmailField()
    check_in = models.CharField(max_length=50)
    check_out = models.CharField(max_length=50)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking #{self.id} for {self.room.name} ({self.user_email})",
