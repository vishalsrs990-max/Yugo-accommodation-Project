# accommodation/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Room
from .dynamodb_client import save_room_to_dynamodb  # our helper


@receiver(post_save, sender=Room)
def sync_room_to_dynamodb(sender, instance, created, **kwargs):
    """
    After a Room is saved:

      1. Get the S3 URL from Django's storage backend (instance.image.url).
         Django/django-storages already uploaded the file to S3 for us.
      2. Store that URL in Room.s3_url (so templates can use it easily).
      3. Write/update an item in DynamoDB (YugoRooms) with S3 URL + metadata.
    """

    # 1) Get S3 URL if image exists
    if instance.image and hasattr(instance.image, "url"):
        s3_url = instance.image.url

        # Avoid infinite recursion: use update() instead of instance.save()
        if instance.s3_url != s3_url:
            Room.objects.filter(pk=instance.pk).update(s3_url=s3_url)
            instance.s3_url = s3_url

    # 2) Always sync metadata to DynamoDB
    save_room_to_dynamodb(instance)