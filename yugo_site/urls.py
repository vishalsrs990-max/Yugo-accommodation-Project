from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views

from accommodation import views as acc_views

urlpatterns = [
    path("admin/", admin.site.urls),

    # authentication
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(template_name="accommodation/login.html"),
        name="login",
    ),
    path(
        "accounts/logout/",
        auth_views.LogoutView.as_view(next_page="home"),
        name="logout",
    ),

    # public pages
    path("", acc_views.home, name="home"),
    path("signup/", acc_views.signup, name="signup"),
    path("rooms/<int:room_id>/book/", acc_views.book_room, name="book_room"),
    path(
        "booking/<int:booking_id>/success/",
        acc_views.booking_success,
        name="booking_success",
    ),

    # booking management
    path(
        "booking/<int:booking_id>/edit/",
        acc_views.edit_booking,
        name="edit_booking",
    ),
    path(
        "booking/<int:booking_id>/cancel/",
        acc_views.cancel_booking,
        name="cancel_booking",
    ),
    path("my-bookings/", acc_views.my_bookings, name="my_bookings"),
    path(
        "booking/<int:booking_id>/delete/",
        acc_views.delete_booking,
        name="delete_booking",
    ),

    # SQS: student support ticket
    path("support/", acc_views.support_ticket, name="support_ticket"),

    # manager / media admin
    path("manager/rooms/", acc_views.manager_room_list, name="manager_room_list"),
    path(
        "manager/rooms/<int:room_id>/image/",
        acc_views.manage_room_image,
        name="manage_room_image",
    ),

    # manager: SQS next ticket
    path(
        "manager/support/next/",
        acc_views.manager_next_ticket,
        name="manager_next_ticket",
    ),
]
