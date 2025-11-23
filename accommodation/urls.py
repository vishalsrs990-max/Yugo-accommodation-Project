# accommodation/urls.py

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

    # Auth URLs
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
