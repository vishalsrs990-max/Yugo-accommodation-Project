from django import forms
from .models import Room


class RoomImageForm(forms.ModelForm):
    """
    Simple form used by the custom media admin to upload / change a room image.
    Saving this form updates Room.image, which uses your S3 storage backend.
    """
    class Meta:
        model = Room
        fields = ["image"]
