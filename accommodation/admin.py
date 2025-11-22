from django.contrib import admin
from .models import Room, Booking


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("name", "room_type", "price_per_night", "available", "created_at")
    list_filter = ("room_type", "available")
    search_fields = ("name", "location", "description")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "room", "user_email", "check_in", "check_out", "total_price", "status", "created_at")
    list_filter = ("status", "room")
    search_fields = ("user_email", "room__name")
