from django import forms
from .models import Room


class RoomImageForm(forms.ModelForm):
    """
    Simple form used by the media manager to upload/update
    a single image for a room.
    """
    class Meta:
        model = Room
        fields = ["image"]  # this matches Room.image field


class SupportTicketForm(forms.Form):
    """
    Form for students to raise maintenance/support tickets.
    This data will be sent as a JSON message into the SQS queue.
    """
    name = forms.CharField(max_length=100, label="Your name")
    email = forms.EmailField(label="Email")
    room = forms.CharField(
        max_length=50,
        required=False,
        label="Room number/type",
        help_text="e.g. Twin Classic 12A",
    )
    subject = forms.CharField(max_length=150, label="Subject")
    message = forms.CharField(
        widget=forms.Textarea,
        label="Describe your issue",
    )
