from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import Room, Booking
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
from datetime import datetime

def home(request):
    rooms = Room.objects.filter(available=True)
    return render(request, "accommodation/home.html", {"rooms": rooms})

@csrf_exempt
def book_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)

    if request.method == "POST":
        email = request.POST.get("email")
        check_in = request.POST.get("check_in")
        check_out = request.POST.get("check_out")

        # Simple price calc (no complex rules)
        # You can adapt later to your check-in/out library logic
        days = 1
        try:
            d1 = datetime.fromisoformat(check_in).date()
            d2 = datetime.fromisoformat(check_out).date()
            days = max((d2 - d1).days, 1)
        except Exception:
            pass

        total_price = Decimal(days) * room.price_per_night

        booking = Booking.objects.create(
            room=room,
            user_email=email,
            check_in=check_in,
            check_out=check_out,
            total_price=total_price,
            status="confirmed",  # set immediately for demo
        )

        # Call Lambda to send email
        from .lambda_client import invoke_booking_lambda
        invoke_booking_lambda(booking)

        return redirect(reverse("booking_success", args=[booking.id]))

    return render(request, "accommodation/book_room.html", {"room": room})

def booking_success(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, "accommodation/booking_success.html", {"booking": booking})
