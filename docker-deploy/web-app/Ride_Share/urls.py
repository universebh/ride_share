# Ride_Share/urls.py
from django.urls import path

from . import views


urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('profile', views.edit_profile, name='profile'),
    path('createRide/', views.create_ride, name='create_ride'),
    path('createRide/rideCreated/', views.ride_created, name='ride_created'),
    path('joinRide/', views.join_ride, name='join_ride'),
    path('joinRide/searchResult/', views.search_result, name='search_result'),
    path('joinRide/searchResult/<int:joining_ride_id>/', views.into_ride, name='into_ride'),
    path('takeableRides/<int:take_ride_id>/', views.take_ride, name='take_ride'),
    path('takenRides/', views.check_taken_rides, name='taken_rides'),
    path('takenRides/<int:take_ride_id>/', views.taken_ride_detail, name='taken_ride_detail'),
    path('takenRides/<int:take_ride_id>/complete/', views.complete_ride, name='complete_ride'),
    path('takenRidesHistory/', views.check_taken_rides_history, name='taken_rides_history'),
    # path('takeRide/', views.take_ride, name='take_ride'),  # dont use, this line has been given up
    path('ownedRides/', views.check_owned_rides, name='owned_rides'),
    path('ownedRidesHistory/', views.check_owned_rides_history, name='owned_rides_history'),
    path('sharingRides/', views.check_sharing_rides, name='sharing_rides'),
    path('sharingRidesHistory', views.check_sharing_rides_history, name='sharing_rides_history'),
    path('sharingRides/<int:ride_id>/', views.sharing_ride_detail, name='sharing_ride_detail'),
    path('sharingRides/<int:ride_id>/edit/', views.edit_sharing_ride, name='edit_sharing_ride'),
    path('sharingRides/<int:ride_id>/cancel/', views.cancel_sharing_ride, name='cancel_sharing_ride'),
    path('driverRegistration/', views.driver_registration, name='driver_registration'),
    path('takeableRides/', views.search_takeable_rides, name='search_takeable_rides'),
    path('ownedRides/<int:ride_id>/', views.owned_ride_status, name='owned_ride_status'),
    path('ownedRides/<int:ride_id>/edit/', views.edit_owner_ride, name='edit_owner_ride'),
    path('ownedRides/<int:ride_id>/cancel/', views.cancel_owner_ride, name='cancel_owner_ride'),
    path('', views.home, name='home'),
]