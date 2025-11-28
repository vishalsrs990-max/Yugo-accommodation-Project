from decimal import Decimal
from datetime import datetime
import json

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required, user_passes_test

from .models import Room, Booking
from .forms import RoomImageForm, SupportTicketForm

# SQS demo classes from your zip
from producer import Producer
from consumer import Consumer

# Your reusable pricing library
from yugo_booking_lib.booking_price import BookingPrice


# ---------------------------------------------------------------------
# PUBLIC VIEWS (HOME + BOOKING + SIGNUP)
# ---------------------------------------------------------------------


def home(request):
    # Show ALL rooms; template already uses room.available to show status
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

        # -------------------------------
        # Use BookingPrice library here
        # -------------------------------
        bp = BookingPrice()

        try:
            nights = bp.calculate_nights(check_in, check_out)  # returns 0 if invalid/order wrong
            if nights <= 0:
                nights = 1  # keep same behaviour as before: minimum 1 night
        except Exception:
            nights = 1  # if parsing fails, fall back to 1 night

        total_float = bp.calculate_total_price(
            nights=nights,
            nightly_rate=float(room.price_per_night),
            tax_rate=0.08,   # set VAT here later if you want
            fixed_fee=50.0,
        )

        # Store as Decimal in the DB
        total_price = Decimal(str(total_float))

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

    # Use your library to compute nights from check-in / check-out
    bp = BookingPrice()
    nights = 0
    try:
        nights = bp.calculate_nights(
            str(booking.check_in),   # e.g. "2025-11-28"
            str(booking.check_out),  # e.g. "2025-12-05"
        )
    except Exception:
        # if anything goes wrong, keep nights = 0
        pass

    return render(
        request,
        "accommodation/booking_success.html",
        {
            "booking": booking,
            "nights": nights,   # 👈 this is what your template prints
        },
    )


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


# ---------------------------------------------------------------------
# BOOKING MANAGEMENT (USER CRUD)
# ---------------------------------------------------------------------


@login_required
def edit_booking(request, booking_id):
    """Allow user to update check-in / check-out for an existing booking."""
    booking = get_object_or_404(Booking, id=booking_id)
    room = booking.room

    if request.method == "POST":
        check_in = request.POST.get("check_in")
        check_out = request.POST.get("check_out")

        # -------------------------------
        # Use BookingPrice library again
        # -------------------------------
        bp = BookingPrice()

        try:
            nights = bp.calculate_nights(check_in, check_out)
            if nights <= 0:
                nights = 1
        except Exception:
            nights = 1

        total_float = bp.calculate_total_price(
            nights=nights,
            nightly_rate=float(room.price_per_night),
            tax_rate=0.0,
            fixed_fee=0.0,
        )
        total_price = Decimal(str(total_float))

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
    booking_qs = Booking.objects.filter(id=booking_id)

    if request.method == "POST":
        if booking_qs.exists():
            booking_qs.delete()
        return redirect("my_bookings")

    booking = booking_qs.first()
    if not booking:
        return redirect("my_bookings")

    return render(
        request,
        "accommodation/delete_booking_confirm.html",
        {"booking": booking},
    )


# ---------------------------------------------------------------------
# SQS SUPPORT TICKETS (STUDENT PRODUCER + MANAGER CONSUMER)
# ---------------------------------------------------------------------


@csrf_exempt  # avoid CSRF/origin issues on Cloud9 for now
def support_ticket(request):
    """
    Student view: raise a maintenance/support ticket.
    Uses the tutorial Producer class to send a JSON message to SQS queue
    'yugo-support-queue'.
    """
    if request.method == "POST":
        form = SupportTicketForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            data["created_at"] = datetime.utcnow().isoformat()

            # Turn dict into JSON string and send to queue yugo-support-queue
            message = json.dumps(data)
            p = Producer()
            p.send_message("yugo-support-queue", message)

            return render(
                request,
                "accommodation/support_ticket_success.html",
                {"ticket": data},
            )
    else:
        form = SupportTicketForm()

    return render(
        request,
        "accommodation/support_ticket_form.html",
        {"form": form},
    )


# ------------- MEDIA ADMIN (custom, separate from Django admin) ------------- #


def _is_media_admin(user):
    """
    Only allow staff users (e.g. your 'manager' account) to manage images
    and support tickets.
    Normal users cannot access these URLs.
    """
    return user.is_staff


@login_required
@user_passes_test(_is_media_admin)
def manager_room_list(request):
    """
    Simple dashboard: list all rooms so a media admin can manage images.
    """
    rooms = Room.objects.all().order_by("id")
    return render(
        request,
        "accommodation/manager_room_list.html",
        {"rooms": rooms},
    )


@login_required
@user_passes_test(_is_media_admin)
def manage_room_image(request, room_id):
    """
    Upload or delete an image for a specific room.

    Saving/deleting room.image uses your existing S3 storage backend,
    so no new IAM roles are needed.
    """
    room = get_object_or_404(Room, id=room_id)

    if request.method == "POST":
        # If the 'Delete image' button was pressed:
        if "delete_image" in request.POST:
            if room.image:
                # delete from S3 and clear the field, but don't delete the room
                room.image.delete(save=False)
                room.image = None
                room.save()
            return redirect("manager_room_list")

        # Otherwise it's an upload/update
        form = RoomImageForm(request.POST, request.FILES, instance=room)
        if form.is_valid():
            form.save()  # uploads to S3 via your configured storage
            return redirect("manager_room_list")
    else:
        form = RoomImageForm(instance=room)

    return render(
        request,
        "accommodation/manager_room_image.html",
        {"room": room, "form": form},
    )


@login_required
@user_passes_test(_is_media_admin)
@csrf_exempt
def manager_next_ticket(request):
    """
    Manager-only view: fetch and delete the next support ticket
    message from the SQS queue using the Consumer class.
    """
    result_message = None

    if request.method == "POST":
        c = Consumer()
        # This will:
        # - get queue URL for 'yugo-support-queue'
        # - receive one message
        # - print it in the terminal
        # - delete it from the queue
        c.consume_message("yugo-support-queue")
        result_message = (
            "Next support ticket has been consumed and removed from the SQS queue. "
            "Check the Cloud9 terminal logs for full ticket details (printed by Consumer)."
        )

    return render(
        request,
        "accommodation/manager_next_ticket.html",
        {"result_message": result_message},
    )