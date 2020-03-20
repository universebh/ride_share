# Ride_Share/views.py
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from .forms import SignupForm, RideCreationForm, JoinRideForm, driverRegistrationForm, sharerEdittingForm
from .forms import UserProfileEditForm, DriverProfileEditForm, RideEditForm
from .models import Ride, MyUser, Sharer, RegisteredSharer, Vehicle
import datetime
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .global_vars import REVERSE_RIDE_STATUS_
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail
from django.db.models import Q
from django.http import Http404
import sys

# Create your views here.
def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            # messages.success(request, 'Account created successfully')
            return redirect('login')
    else:
        form = SignupForm()
    return render(request, 'signup.html', context={'form': form})


@login_required(login_url='../accounts/login/')
def edit_profile(request):
    user = get_object_or_404(MyUser, pk=request.user.id)
    has_taken_ride = False
    if user.plate_num and Ride.objects.filter(driver=request.user).exclude(ride_status='cop'):
        has_taken_ride = True
    if request.method == 'POST':
        if not user.plate_num or has_taken_ride:
            form = UserProfileEditForm(request.POST)
        else:
            form = DriverProfileEditForm(request.POST, vehicle=Vehicle, myself=request.user)
        if form.is_valid():
            user.email = form.cleaned_data['email']
            if user.plate_num and not has_taken_ride:
                todelete = get_object_or_404(Vehicle, pk=user.plate_num.plate_num)
                todelete.delete()
                vehicle = Vehicle()
                vehicle.plate_num = form.cleaned_data['plate_num']
                vehicle.type = form.cleaned_data['vehicle_type']
                vehicle.capacity = form.cleaned_data['capacity']
                vehicle.special_vehicle_info = form.cleaned_data['special_vehicle_info']
                vehicle.save()
                user.plate_num = vehicle 
            user.save()
            return render(request, 'profile_changed.html')
    else:
        if not user.plate_num or has_taken_ride:
            form = UserProfileEditForm(initial={'email': user.email,})
        else:
            form = DriverProfileEditForm(vehicle=Vehicle, myself=request.user,
            initial={
                'email': user.email, 'plate_num': user.plate_num.plate_num, 
                'vehicle_type': user.plate_num.type, 'capacity':request.user.plate_num.capacity,
                'special_vehicle_info': user.plate_num.special_vehicle_info})
    return render(request, 'profile.html', {
        'form': form, 'user': user, 'has_taken_ride': has_taken_ride})


@login_required(login_url='../accounts/login/')
def create_ride(request):
    ride = Ride()
    if request.method == 'POST':
        form = RideCreationForm(request.POST)
        if form.is_valid():
            ride.dest = form.cleaned_data['dest']
            ride.pickup_time = form.cleaned_data['pickup_time']
            ride.owner_pass_num = form.cleaned_data['owner_pass_num']
            ride.sharable = form.cleaned_data['sharable']
            ride.actual_pass_num = ride.owner_pass_num
            ride.owner = request.user
            ride.vehicle_type = form.cleaned_data['vehicle_type']
            ride.avail_seats = 200000
            ride.special_requests = form.cleaned_data['special_requests']
            ride.save()
            return HttpResponseRedirect(reverse('ride_created'))
    else:
        proposed_pickup_time = timezone.now()
        form = RideCreationForm(
            initial={'pickup_time': proposed_pickup_time, 'owner_pass_num': 1, 'special_requests': ''})
    
    return render(request, 'create_ride.html', {'form': form, 'ride':ride})


def home(request):
    return render(request, "home.html")


@login_required(login_url='../accounts/login/')
def join_ride(request):
    sharer = Sharer()
    if request.method == 'POST':
        form = JoinRideForm(request.POST)
        if form.is_valid():
            sharer.pass_num = form.cleaned_data['number_of_passengers']
            sharer.earliest_date_time = form.cleaned_data['earliest_pickup_time']
            sharer.latest_date_time = form.cleaned_data['latest_pickup_time']
            # if sharer.earliest_date_time >= sharer.latest_date_time:
            #      raise ValidationError(_('Invalid latest datetime - should be greater than earliest datetime!'))
            sharer.dest = form.cleaned_data['destination']
            sharer.sharerid = request.user
            # sharer.special_requests = form.cleaned_data['special_requests']
            sharer.save()
            return HttpResponseRedirect(reverse('search_result'))
    else:
        proposed_pickup_time = timezone.now()
        form = JoinRideForm(
            initial={
                'earliest_pickup_time': proposed_pickup_time, 
                'latest_pickup_time': proposed_pickup_time,
                'number_of_passengers': 1,
            }
        )
    return render(request, 'join_ride.html', context={'form': form})


# def take_ride(request):
#     return render(request, 'takeable_rides.html')


def ride_created(request):
    return render(request, "ride_created.html")


@login_required(login_url='../accounts/login/')
def search_result(request):
    sharer = get_object_or_404(Sharer, pk=request.user)
    sharearable_rides = Ride.objects.filter(
        ride_status='opn',
        sharable=True,
        dest=sharer.dest, 
        pickup_time__gte=sharer.earliest_date_time,
        pickup_time__lte=sharer.latest_date_time,
        avail_seats__gte=sharer.pass_num,
        # special_requests=sharer.special_requests,
    ).exclude(owner=request.user).exclude(share_id=request.user).exclude(driver=request.user).order_by('ride_status')
    if sharearable_rides.exists() == False:
        return render(request, "no_search_result.html")
    page = request.GET.get('page', 1)
    paginator = Paginator(sharearable_rides, 3)
    try:
        sharearable_rides = paginator.page(page)
    except PageNotAnInteger:
        sharearable_rides = paginator.page(1)
    except EmptyPage:
        sharearable_rides = paginator.page(paginator.num_pages)
    return render(
        request, "search_result.html", context={'sharearable_rides': sharearable_rides})
        

@login_required(login_url='../accounts/login/')
def check_owned_rides(request):
    owned_rides = Ride.objects.filter(owner=request.user).exclude(ride_status="cop").order_by('ride_status')
    if owned_rides.exists() == False:
        return render(request, "no_owned_rides.html")
    page = request.GET.get('page', 1)
    paginator = Paginator(owned_rides, 3)
    try:
        owned_rides = paginator.page(page)
    except PageNotAnInteger:
        owned_rides = paginator.page(1)
    except EmptyPage:
        owned_rides = paginator.page(paginator.num_pages)
    return render(request, "owned_rides.html", context={'owned_rides': owned_rides})


@login_required(login_url='../accounts/login/')
def check_owned_rides_history(request):
    owned_rides = Ride.objects.filter(owner=request.user, ride_status="cop").order_by('pickup_time')
    if owned_rides.exists() == False:
        return render(request, "no_owned_rides.html")
    page = request.GET.get('page', 1)
    paginator = Paginator(owned_rides, 3)
    try:
        owned_rides = paginator.page(page)
    except PageNotAnInteger:
        owned_rides = paginator.page(1)
    except EmptyPage:
        owned_rides = paginator.page(paginator.num_pages)
    return render(request, "owned_rides_history.html", context={'owned_rides': owned_rides})


@login_required(login_url='../accounts/login/')
def check_sharing_rides(request):
    # if not RegisteredSharer.objects.filter(registered_sharer_id=request.user).exists():
    #     return render(request, "no_sharing_rides.html")

    # if not Ride.objects.filter(share_id=request.user).exclude(ride_status="cop").exists():
    #     return render(request, "no_sharing_rides.html")
    sharing_rides = Ride.objects.filter(share_id=request.user).exclude(ride_status="cop").order_by('ride_status')
    if not sharing_rides.exists():
        return render(request, "no_sharing_rides.html")
    page = request.GET.get('page', 1)
    paginator = Paginator(sharing_rides, 3)
    try:
        sharing_rides = paginator.page(page)
    except PageNotAnInteger:
        sharing_rides = paginator.page(1)
    except EmptyPage:
        sharing_rides = paginator.page(paginator.num_pages)
    return render(request, "sharing_rides.html", context={'sharing_rides': sharing_rides})


@login_required(login_url='../accounts/login/')
def check_sharing_rides_history(request):
    # if not RegisteredSharer.objects.filter(registered_sharer_id=request.user).exists():
    #     return render(request, "no_sharing_rides.html")

    # if not Ride.objects.filter(share_id=request.user).exclude(ride_status="cop").exists():
    #     return render(request, "no_sharing_rides.html")
    sharing_rides = Ride.objects.filter(share_id=request.user, ride_status="cop").order_by('ride_status')
    if not sharing_rides.exists():
        return render(request, "no_sharing_rides.html")
    page = request.GET.get('page', 1)
    paginator = Paginator(sharing_rides, 3)
    try:
        sharing_rides = paginator.page(page)
    except PageNotAnInteger:
        sharing_rides = paginator.page(1)
    except EmptyPage:
        sharing_rides = paginator.page(paginator.num_pages)
    return render(request, "sharing_rides.html", context={'sharing_rides': sharing_rides})


@login_required(login_url='../accounts/login/')
def into_ride(request, joining_ride_id):
    # print("---------------------------------", type(joining_ride_id))
    sharing_ride = get_object_or_404(Ride, pk=joining_ride_id)
    sharer = get_object_or_404(Sharer, pk=request.user)
    
    # sharing_ride.share_id = request.user
    sharing_ride.share_id.add(request.user)

    sharing_ride.actual_pass_num += sharer.pass_num
    sharing_ride.avail_seats -= sharer.pass_num
    sharing_ride.save()
    sharer.delete()
    registeredSharer = RegisteredSharer(registered_sharer_id=request.user, rideid=sharing_ride, pass_num=sharer.pass_num)
    registeredSharer.save()
    # if RegisteredSharer.objects.filter(registered_sharer_id=request.user).exists() == False:
    #     registeredSharer = RegisteredSharer(registered_sharer_id=request.user)
    #     registeredSharer.save()
    
    return render(request, "successfully_joined.html")


@login_required(login_url='../accounts/login/')
def driver_registration(request):
    user = get_object_or_404(MyUser, pk=request.user.id)
    vehicle = Vehicle()
    if request.method == 'POST':
        form = driverRegistrationForm(request.POST, vehicle=Vehicle)
        if form.is_valid():
            vehicle.plate_num = form.cleaned_data['plate_num']
            vehicle.type = form.cleaned_data['vehicle_type']
            vehicle.capacity = form.cleaned_data['capacity']
            vehicle.special_vehicle_info = form.cleaned_data['special_vehicle_info']
            vehicle.save()
            # vehicle = get_object_or_404(Vehicle, pk=form.cleaned_data['plate_num'])
            user.plate_num = vehicle
            user.save()
            return render(request, 'driver_register_succeed.html')
    else:
        form = driverRegistrationForm(vehicle=Vehicle)
    
    return render(request, 'driver_registration.html', context={'form':form})


@login_required(login_url='../accounts/login/')
def search_takeable_rides(request):
    user = get_object_or_404(MyUser, pk=request.user.id)
    vehicle = user.plate_num
    takeable_rides = Ride.objects.filter(
        Q(vehicle_type=vehicle.type)|Q(vehicle_type=""), driver__isnull=True, 
        special_requests=vehicle.special_vehicle_info).exclude(owner=request.user).exclude(
            share_id__exact=request.user).exclude(ride_status="cop").exclude(
                actual_pass_num__gt=request.user.plate_num.capacity - 1).order_by('ride_status')
    if takeable_rides.exists() == False:
        return render(request, "no_takable_rides.html")
    page = request.GET.get('page', 1)
    paginator = Paginator(takeable_rides, 3)
    try:
        takeable_rides = paginator.page(page)
    except PageNotAnInteger:
        takeable_rides = paginator.page(1)
    except EmptyPage:
        takeable_rides = paginator.page(paginator.num_pages)
    return render(request, 'takeable_rides.html', context={'takeable_rides':takeable_rides})


@login_required(login_url='../accounts/login/')
def take_ride(request, take_ride_id):
    # if not request.user.plate_num:
    #     raise ValidationError(_('You must become a driver to take a ride!'))
    ride_to_take = get_object_or_404(Ride, pk=take_ride_id)
    ride_to_take.driver = request.user
    ride_to_take.ride_status = 'con'
    # if ride_to_take.vehicle_type == "":
    ride_to_take.avail_seats = request.user.plate_num.capacity - 1 - ride_to_take.actual_pass_num
    ride_to_take.vehicle_type = request.user.plate_num.type
    
    ride_to_take.save()

    owner = ride_to_take.owner
    dest = ride_to_take.dest
    driver_user_name = ride_to_take.driver
    vehicle_type = ride_to_take.driver.plate_num.type
    vehicle_plate_num = ride_to_take.driver.plate_num.plate_num
    pickup_time = ride_to_take.pickup_time
    send_mail(
        'Owned Ride Confirmed',
        'Hi {},\n\nYour owned ride to {}'.format(owner, dest) + \
            ' has been confirmed by driver {}'.format(driver_user_name) + \
            ' with vehicle type {} plated {}'.format(vehicle_type, vehicle_plate_num) + \
            ', and is supoosed to pick you up at {}.'.format(pickup_time) + \
            '\n\nThanks!',
        'erss.hwk1.wx50.cz130@gmail.com',
        [owner.email],
        fail_silently=False,
    )
    # sharers = Sharer.objects.filter(sharerid=ride_to_take.share_id)
    sharers = RegisteredSharer.objects.filter(rideid=ride_to_take)
    if sharers:
        sharer_emails = [usr.registered_sharer_id.email for usr in sharers]
        # sharer_emails = []
        # for user in sharers.iterator():
        send_mail(
            'Shared Ride Confirmed',
            'Hi {},\n\nYour shared ride to {}'.format(owner, dest) + \
                ' has been confirmed by driver {}'.format(driver_user_name) + \
                ' with vehicle type {} plated {}'.format(vehicle_type, vehicle_plate_num) + \
                ', and is supoosed to pick you up at {}.'.format(pickup_time) + \
                '\n\nThanks!',
            'erss.hwk1.wx50.cz130@gmail.com',
            sharer_emails,
            fail_silently=False,
        )
    
    return render(request, "successfully_taken.html")


@login_required(login_url='../accounts/login/')
def owned_ride_status(request, ride_id):
    owned_ride_status = get_object_or_404(Ride, pk=ride_id, owner=request.user)
    owner_name = owned_ride_status.owner.username
    driver = None
    if not owned_ride_status.driver:
        driver = "No driver yet"
    else:
        # driver = owned_ride_status.driver.username
        driver = owned_ride_status.driver
    # if not owned_ride_status.share_id:
    #     sharer = "No sharer yet"
    # else:
    sharer = owned_ride_status.share_id.all()
    destination = owned_ride_status.dest
    num_owner_pass = owned_ride_status.owner_pass_num
    num_pass = owned_ride_status.actual_pass_num
    num_sharer_pass = owned_ride_status.actual_pass_num - owned_ride_status.owner_pass_num
    ride_status = REVERSE_RIDE_STATUS_[owned_ride_status.ride_status]
    pickup_time = owned_ride_status.pickup_time
    special_requests = owned_ride_status.special_requests
    vehicle_type = owned_ride_status.vehicle_type

    if owned_ride_status.sharable == True:
        return render(request, 'owner_ride_status_sharer.html', 
                    context={'owner_name': owner_name, 'driver': driver,
                                'sharer': sharer, 'destination': destination,
                                'num_pass':num_pass, 'num_sharer_pass':num_sharer_pass,
                                'num_owner_pass': num_owner_pass,
                                'ride_status':ride_status, 'pickup_time': pickup_time,
                                'special_requests': special_requests,
                                'vehicle_type': vehicle_type})
    else:
         return render(request, 'owner_ride_status_no_sharer.html', 
                    context={'owner_name': owner_name, 'driver': driver,
                                'destination': destination,
                                'num_pass':num_pass,
                                'ride_status':ride_status, 
                                'special_requests': special_requests,
                                'vehicle_type': vehicle_type})       


@login_required(login_url='../accounts/login/')
def edit_owner_ride(request, ride_id):
    ride = get_object_or_404(Ride, pk=ride_id, owner=request.user)
    if request.method == 'POST':
        # form = RideEditForm(request.POST, ride=ride, initial={
        #         'dest': ride.dest, 'pickup_time': ride.pickup_time, 
        #         'owner_pass_num': ride.owner_pass_num, 'sharable': ride.sharable,
        #         'vehicle_type': ride.vehicle_type, 'special_requests': ride.special_requests},) if ride.sharable else RideCreationForm(request.POST)
        form = RideEditForm(request.POST, ride=ride) if ride.sharable else RideCreationForm(request.POST)
        if form.is_valid():
            ride.dest = form.cleaned_data['dest']
            ride.pickup_time = form.cleaned_data['pickup_time']
            old_owner_pass_num = ride.owner_pass_num
            ride.owner_pass_num = form.cleaned_data['owner_pass_num']
            if not ride.sharable:
                ride.sharable = form.cleaned_data['sharable']
            # ride.actual_pass_num = ride.owner_pass_num
            ride.actual_pass_num += ride.owner_pass_num - old_owner_pass_num
            ride.owner = request.user
            ride.vehicle_type = form.cleaned_data['vehicle_type']
            if ride.driver:
                ride.avail_seats = ride.driver.plate_num.capacity - 1 - ride.actual_pass_num
            else:
                ride.avail_seats = 200000
            ride.special_requests = form.cleaned_data['special_requests']
            ride.save()
            sharers = ride.share_id.all()
            if sharers:
                sharer_emails = [usr.email for usr in sharers]
                send_mail(
                    'Ride Edited!',
                    'Hi sharer,\n\nYour sharing ride with {} ride to {}'.format(ride.owner.username, ride.dest) + \
                        ' has been edited by the owner {}'.format(ride.owner.username) + \
                        ' Please visit our website to view the changes.',
                    'erss.hwk1.wx50.cz130@gmail.com',
                    sharer_emails,
                    fail_silently=False,
                ) 
            return render(request, 'edit_successfully.html')

            # sharers = RegisteredSharer.objects.filter(rideid=ride)
    else:
        proposed_pickup_time = timezone.now()
        if ride.sharable:
            form = RideEditForm(initial={
                'dest': ride.dest, 'pickup_time': ride.pickup_time, 
                'owner_pass_num': ride.owner_pass_num, 'sharable': ride.sharable,
                'vehicle_type': ride.vehicle_type, 'special_requests': ride.special_requests}, ride=ride)
        else:
            form = RideCreationForm(initial={
                'dest': ride.dest, 'pickup_time': ride.pickup_time, 
                'owner_pass_num': ride.owner_pass_num, 'sharable': ride.sharable,
                'vehicle_type': ride.vehicle_type, 'special_requests': ride.special_requests})
    
    return render(request, 'edit_owner_ride.html', {'form': form, 'ride':ride})


@login_required(login_url='../accounts/login/')
def check_taken_rides(request):
    taken_rides = Ride.objects.filter(driver=request.user).exclude(
        ride_status="cop").order_by('ride_status')
    if taken_rides.exists() == False:
        return render(request, "no_taken_rides.html")
    page = request.GET.get('page', 1)
    paginator = Paginator(taken_rides, 3)
    try:
        taken_rides = paginator.page(page)
    except PageNotAnInteger:
        taken_rides = paginator.page(1)
    except EmptyPage:
        taken_rides = paginator.page(paginator.num_pages)
    return render(request, "taken_rides.html", context={'taken_rides': taken_rides})


@login_required(login_url='../accounts/login/')
def taken_ride_detail(request, take_ride_id):
    taken_ride = get_object_or_404(Ride, pk=take_ride_id, driver=request.user)
    owner_name = taken_ride.owner.username
    if not taken_ride.share_id:
        sharer = "No sharer yet"
    else:
        sharer = taken_ride.share_id.all()
    destination = taken_ride.dest
    num_owner_pass = taken_ride.owner_pass_num
    num_pass = taken_ride.actual_pass_num
    num_sharer_pass = taken_ride.actual_pass_num - taken_ride.owner_pass_num
    ride_status = REVERSE_RIDE_STATUS_[taken_ride.ride_status]
    pickup_time = taken_ride.pickup_time
    special_requests = taken_ride.special_requests

    if taken_ride.sharable == True:
        return render(request, 'taken_ride_detail_sharer.html', 
                    context={'owner_name': owner_name, 'sharer': sharer, 
                            'destination': destination, 'num_pass':num_pass, 
                            'num_sharer_pass':num_sharer_pass,'num_owner_pass': num_owner_pass,
                            'ride_status':ride_status, 'pickup_time': pickup_time,
                            'special_requests': special_requests})
    else:
         return render(request, 'taken_ride_detail_no_sharer.html', 
                    context={'owner_name': owner_name,
                                'destination': destination,
                                'num_pass':num_pass,
                                'ride_status':ride_status,
                                'special_requests': special_requests})   


@login_required(login_url='../accounts/login/')
def complete_ride(request, take_ride_id):
    # if not request.user.plate_num:
    #     raise ValidationError(_('You must become a driver to take a ride!'))
    ride_to_take = get_object_or_404(Ride, pk=take_ride_id, driver=request.user)
    ride_to_take.ride_status = 'cop'
    ride_to_take.save()

    owner, sharers = ride_to_take.owner, ride_to_take.share_id
    dest = ride_to_take.dest
    driver_user_name = ride_to_take.driver
    vehicle_type = ride_to_take.driver.plate_num.type
    vehicle_plate_num = ride_to_take.driver.plate_num.plate_num
    pickup_time = ride_to_take.pickup_time
    send_mail(
        'Owned Ride Completed',
        'Hi {},\n\nYour owned ride to {}'.format(owner, dest) + \
            ' confirmed by driver {}'.format(driver_user_name) + \
            ' with vehicle type {} plated {}'.format(vehicle_type, vehicle_plate_num) + \
            ' was completed.' + \
            '\n\nThanks!',
        'erss.hwk1.wx50.cz130@gmail.com',
        [owner.email],
        fail_silently=False,
    )
    sharers = RegisteredSharer.objects.filter(rideid=ride_to_take)
    if sharers:
        sharer_emails = [usr.registered_sharer_id.email for usr in sharers]
        send_mail(
            'Shared Ride Completed',
            'Hi {},\n\nYour shared ride to {}'.format(owner, dest) + \
                ' confirmed by driver {}'.format(driver_user_name) + \
                ' with vehicle type {} plated {}'.format(vehicle_type, vehicle_plate_num) + \
                ' was completed.' + \
                '\n\nThanks!',
            'erss.hwk1.wx50.cz130@gmail.com',
            sharer_emails,
            fail_silently=False,
        )
    return render(request, "successfully_complete.html")


@login_required(login_url='../accounts/login/')
def cancel_owner_ride(request, ride_id):
    ride = get_object_or_404(Ride, pk=ride_id, owner=request.user)
    if ride.driver != None:
        send_mail(
            'Ride CANCELLED!',
            'Hi {},\n\nYour taken ride to {}'.format(ride.driver.username, ride.dest) + \
                ' has been CANCELLED by the owner {}'.format(ride.owner.username),
            'erss.hwk1.wx50.cz130@gmail.com',
            [ride.driver.email],
            fail_silently=False,
        )
    sharers = RegisteredSharer.objects.filter(rideid=ride)
    RegisteredSharer.objects.filter(rideid=ride_id).delete()
    if sharers:
        sharer_emails = [usr.registered_sharer_id.email for usr in sharers]
        send_mail(
            'Ride CANCELLED!',
            'Hi sharer,\n\nYour sharing ride with {} ride to {}'.format(ride.owner.username, ride.dest) + \
                ' has been CANCELLED by the owner {}'.format(ride.owner.username),
            'erss.hwk1.wx50.cz130@gmail.com',
            sharer_emails,
            fail_silently=False,
        )        
    Ride.objects.filter(ride_id=ride_id).delete()
    return render(request, 'cancelled_successfully.html')


@login_required(login_url='../accounts/login/')
def sharing_ride_detail(request, ride_id):
    sharing_ride_detail = get_object_or_404(Ride, pk=ride_id, share_id=request.user)
    owner_name = sharing_ride_detail.owner.username
    driver = None
    if not sharing_ride_detail.driver:
        driver = "No driver yet"
    else:
        # driver = sharing_ride_detail.driver.username
        driver = sharing_ride_detail.driver

    destination = sharing_ride_detail.dest
    num_pass = sharing_ride_detail.actual_pass_num
    num_owner_pass = sharing_ride_detail.owner_pass_num
    num_sharer_pass = sharing_ride_detail.actual_pass_num - sharing_ride_detail.owner_pass_num
    ride_status = REVERSE_RIDE_STATUS_[sharing_ride_detail.ride_status]
    special_requests = sharing_ride_detail.special_requests
    vehicle_type = sharing_ride_detail.vehicle_type

    sharer = sharing_ride_detail.share_id.all()
    return render(request, 'sharing_ride_detail.html', 
                context={'owner_name': owner_name, 'driver': driver, 'sharer': sharer,
                            'destination': destination, 'num_pass':num_pass, 
                            'num_sharer_pass':num_sharer_pass,
                            'num_owner_pass':num_owner_pass,
                            'ride_status':ride_status, 'special_requests': special_requests,
                            'vehicle_type': vehicle_type})


@login_required(login_url='../accounts/login/')
def edit_sharing_ride(request, ride_id):
    ride = get_object_or_404(Ride, pk=ride_id)
    sharer = get_object_or_404(RegisteredSharer, rideid=ride_id, registered_sharer_id=request.user)
    # print("------------", sharer.pass_num)
    if request.method == 'POST':
        form = sharerEdittingForm(request.POST, ride=ride, sharer=sharer)
        if form.is_valid():
            old_pass_num =sharer.pass_num
            new_sharing_pass_num = form.cleaned_data['new_passenger_number']
            ride.actual_pass_num += new_sharing_pass_num - old_pass_num
            if ride.driver:
                ride.avail_seats = ride.driver.plate_num.capacity - 1 - ride.actual_pass_num
            ride.save()
            sharer.pass_num = new_sharing_pass_num
            sharer.save()
            return render(request, 'edit_successfully_sharer.html')
    else:
        form = sharerEdittingForm(initial={'new_passenger_number': sharer.pass_num}, ride=ride, sharer=sharer)    
    return render(request, 'edit_sharer_ride.html', {'form': form, 'ride':ride})
    
@login_required(login_url='../accounts/login/')
def cancel_sharing_ride(request, ride_id):
    ride = get_object_or_404(Ride, pk=ride_id)
    # send_mail(
    #     'Ride CANCELLED!',
    #     'Hi {},\n\nYour sharing ride with {} ride to {}'.format(request.user.username, ride.owner.username, ride.dest) + \
    #         ' has been successfully CANCELLED.',
    #     'erss.hwk1.wx50.cz130@gmail.com',
    #     [request.user.email],
    #     fail_silently=False,
    # )
    
    sharer = get_object_or_404(RegisteredSharer,rideid=ride_id, registered_sharer_id=request.user)
    ride.actual_pass_num -= sharer.pass_num
    ride.avail_seats += sharer.pass_num
    ride.share_id.remove(request.user)
    ride.save()
    sharer.delete()

    # Owner and other sharers will receive email
    
    # send_mail(
    #         'Ride CANCELLED!',
    #         'Hi {},\n\nYour owned ride to {}'.format(ride.owner.username, ride.dest) + \
    #             ' has one or more sharer(s) quit.',
    #         'erss.hwk1.wx50.cz130@gmail.com',
    #         [ride.driver.email],
    #         fail_silently=False,
    #     )    

    # sharers = RegisteredSharer.objects.filter(rideid=ride)
    
    # if sharers:
    #     sharer_emails = [usr.registered_sharer_id.email for usr in sharers]
    #     send_mail(
    #         'Ride CANCELLED!',
    #         'Hi sharer,\n\nYour sharing ride with {} ride to {}'.format(ride.owner.username, ride.dest) + \
    #             ' has been CANCELLED by the owner {}'.format(ride.owner.username),
    #         'erss.hwk1.wx50.cz130@gmail.com',
    #         sharer_emails,
    #         fail_silently=False,
    #     )     
     

    return render(request, 'cancelled_successfully_sharer.html')


@login_required(login_url='../accounts/login/')
def check_taken_rides_history(request):
    taken_rides = Ride.objects.filter(driver=request.user, ride_status="cop").order_by('pickup_time')
    if taken_rides.exists() == False:
        return render(request, "no_taken_rides.html")
    page = request.GET.get('page', 1)
    paginator = Paginator(taken_rides, 3)
    try:
        taken_rides = paginator.page(page)
    except PageNotAnInteger:
        taken_rides = paginator.page(1)
    except EmptyPage:
        taken_rides = paginator.page(paginator.num_pages)
    return render(request, "taken_rides_history.html", context={'taken_rides': taken_rides})


