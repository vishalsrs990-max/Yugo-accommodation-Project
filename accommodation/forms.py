from django import forms
from .models import Room


class RoomImageForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ["image"]


class SupportTicketForm(forms.Form):
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
