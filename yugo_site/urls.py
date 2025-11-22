from django.contrib import admin
from django.urls import path
from accommodation import views as accommodation_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', accommodation_views.home, name='home'),
    path('rooms/<int:room_id>/book/', accommodation_views.book_room, name='book_room'),
    path('booking/<int:booking_id>/success/', accommodation_views.booking_success, name='booking_success'),
]
