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

from producer import Producer
from consumer import Consumer

from yugo_booking_lib.booking_price import BookingPrice


def home(request):
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
            tax_rate=0.08,
            fixed_fee=50.0,
        )

        total_price = Decimal(str(total_float))

        booking = Booking.objects.create(
            room=room,
            user_email=email,
            check_in=check_in,
            check_out=check_out,
            total_price=total_price,
            status="confirmed",
        )

        room.available = False
        room.save()

        from .lambda_client import invoke_booking_lambda
        invoke_booking_lambda(booking)

        return redirect(reverse("booking_success", args=[booking.id]))

    return render(request, "accommodation/book_room.html", {"room": room})


def booking_success(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    bp = BookingPrice()
    nights = 0
    try:
        nights = bp.calculate_nights(
            str(booking.check_in),
            str(booking.check_out),
        )
    except Exception:
        pass

    return render(
        request,
        "accommodation/booking_success.html",
        {
            "booking": booking,
            "nights": nights,
        },
    )


def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect("home")
    else:
        form = UserCreationForm()

    return render(request, "accommodation/signup.html", {"form": form})


@login_required
def edit_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    room = booking.room

    if request.method == "POST":
        check_in = request.POST.get("check_in")
        check_out = request.POST.get("check_out")

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

    return render(
        request,
        "accommodation/edit_booking.html",
        {"booking": booking, "room": room},
    )


@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if request.method == "POST":
        booking.status = "cancelled"
        booking.save()

        room = booking.room
        room.available = True
        room.save()

        return redirect("booking_success", booking_id=booking.id)

    return render(
        request,
        "accommodation/cancel_booking_confirm.html",
        {"booking": booking},
    )


@login_required
def my_bookings(request):
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


@csrf_exempt
def support_ticket(request):
    if request.method == "POST":
        form = SupportTicketForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            data["created_at"] = datetime.utcnow().isoformat()

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


def _is_media_admin(user):
    return user.is_staff


@login_required
@user_passes_test(_is_media_admin)
def manager_room_list(request):
    rooms = Room.objects.all().order_by("id")
    return render(
        request,
        "accommodation/manager_room_list.html",
        {"rooms": rooms},
    )


@login_required
@user_passes_test(_is_media_admin)
def manage_room_image(request, room_id):
    room = get_object_or_404(Room, id=room_id)

    if request.method == "POST":
        if "delete_image" in request.POST:
            if room.image:
                room.image.delete(save=False)
                room.image = None
                room.save()
            return redirect("manager_room_list")

        form = RoomImageForm(request.POST, request.FILES, instance=room)
        if form.is_valid():
            form.save()
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
    result_message = None

    if request.method == "POST":
        c = Consumer()
        c.consume_message("yugo-support-queue")
        result_message = (
            "Next support ticket has been consumed and removed from the SQS queue."
        )

    return render(
        request,
        "accommodation/manager_next_ticket.html",
        {"result_message": result_message},
    )
