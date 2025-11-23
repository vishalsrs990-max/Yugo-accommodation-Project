from decimal import Decimal
from datetime import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required

from .models import Room, Booking


def home(request):
    # show ALL rooms; template uses room.available to show status
    rooms = Room.objects.all().order_by("id")
    return render(request, "accommodation/home.html", {"rooms": rooms})


@csrf_exempt
@login_required
def book_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)

    if request.method == "POST":
        email = request.POST.get("email")
        check_in = request.POST.get("check_in")
        check_out = request.POST.get("check_out")

        # Simple price calc based on nights
        days = 1
        try:
            d1 = datetime.fromisoformat(check_in).date()
            d2 = datetime.fromisoformat(check_out).date()
            days = max((d2 - d1).days, 1)
        except Exception:
            # if parsing fails, fall back to 1 night
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

        # Mark room as not available so it shows as "Not available"
        room.available = False
        room.save()

        # Call Lambda to send email
        from .lambda_client import invoke_booking_lambda
        invoke_booking_lambda(booking)

        return redirect(reverse("booking_success", args=[booking.id]))

    return render(request, "accommodation/book_room.html", {"room": room})


def booking_success(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, "accommodation/booking_success.html", {"booking": booking})


def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # automatically log them in after signup
            auth_login(request, user)
            return redirect("home")
    else:
        form = UserCreationForm()

    return render(request, "accommodation/signup.html", {"form": form})


@login_required
def edit_booking(request, booking_id):
    """Allow user to update check-in / check-out for an existing booking."""
    booking = get_object_or_404(Booking, id=booking_id)
    room = booking.room

    if request.method == "POST":
        check_in = request.POST.get("check_in")
        check_out = request.POST.get("check_out")

        # Reuse same days/price logic as book_room
        days = 1
        try:
            d1 = datetime.fromisoformat(check_in).date()
            d2 = datetime.fromisoformat(check_out).date()
            days = max((d2 - d1).days, 1)
        except Exception:
            pass

        total_price = Decimal(days) * room.price_per_night

        booking.check_in = check_in
        booking.check_out = check_out
        booking.total_price = total_price
        booking.status = "updated"
        booking.save()

        return redirect("booking_success", booking_id=booking.id)

    # GET: show form prefilled
    return render(
        request,
        "accommodation/edit_booking.html",
        {"booking": booking, "room": room},
    )


@login_required
def cancel_booking(request, booking_id):
    """Allow user to cancel an existing booking."""
    booking = get_object_or_404(Booking, id=booking_id)

    if request.method == "POST":
        booking.status = "cancelled"
        booking.save()

        # Put the room back as available so it reappears on homepage
        room = booking.room
        room.available = True
        room.save()

        return redirect("booking_success", booking_id=booking.id)

    # Simple confirmation page
    return render(
        request,
        "accommodation/cancel_booking_confirm.html",
        {"booking": booking},
    )


@login_required
def my_bookings(request):
    """
    Show list of bookings.
    1. Try bookings matching current user's username (often their email).
    2. If none exist, fall back to all bookings so nothing is hidden.
    """
    qs = Booking.objects.filter(user_email=request.user.username)

    if not qs.exists():
        qs = Booking.objects.all()

    bookings = qs.order_by("-created_at")

    return render(
        request,
        "accommodation/my_bookings.html",
        {"bookings": bookings},
    )


@login_required
def delete_booking(request, booking_id):
    """
    Permanently delete a booking from the system.
    This does NOT change room.available, so homepage status stays as-is.
    If the booking does not exist, just redirect back to My bookings.
    """
    # Use .filter() so we don't raise 404 if it doesn't exist
    booking_qs = Booking.objects.filter(id=booking_id)

    if request.method == "POST":
        if booking_qs.exists():
            booking_qs.delete()
        # Whether it existed or not, go back to the list
        return redirect("my_bookings")

    # For GET (if you use a confirmation page)
    booking = booking_qs.first()
    if not booking:
        return redirect("my_bookings")

    return render(
        request,
        "accommodation/delete_booking_confirm.html",
        {"booking": booking},
    )