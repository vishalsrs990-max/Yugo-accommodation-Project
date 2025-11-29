from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Room
from .dynamodb_client import save_room_to_dynamodb


@receiver(post_save, sender=Room)
def sync_room_to_dynamodb(sender, instance, created, **kwargs):
    if instance.image and hasattr(instance.image, "url"):
        s3_url = instance.image.url
        if instance.s3_url != s3_url:
            Room.objects.filter(pk=instance.pk).update(s3_url=s3_url)
            instance.s3_url = s3_url
    save_room_to_dynamodb(instance)
