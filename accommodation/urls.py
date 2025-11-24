from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    # Home page
    path('', views.home, name='home'),

    # Booking URLs
    path('rooms/<int:room_id>/book/', views.book_room, name='book_room'),
    path('booking/<int:booking_id>/success/', views.booking_success, name='booking_success'),
    path('booking/<int:booking_id>/edit/', views.edit_booking, name='edit_booking'),
    path('booking/<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
    path('booking/<int:booking_id>/delete/', views.delete_booking, name='delete_booking'),

    # My bookings list
    path('my-bookings/', views.my_bookings, name='my_bookings'),

    # Custom media admin (separate from Django admin)
    path('manager/rooms/', views.manager_room_list, name='manager_room_list'),
    path('manager/rooms/<int:room_id>/image/', views.manage_room_image, name='manage_room_image'),
    
    # NEW: manager – get next ticket from SQS via Consumer
    path(
        "manager/support/next/",
        acc_views.manager_next_ticket,
        name="manager_next_ticket",
    ),


    # Auth URLs (your existing login/signup)
    path('signup/', views.signup, name='signup'),
    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='accommodation/login.html'
        ),
        name='login',
    ),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
