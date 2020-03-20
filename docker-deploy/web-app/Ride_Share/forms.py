# Ride_Share/forms.py
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.views.generic.edit import CreateView
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import MyUser, Ride, Sharer
import datetime
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator
from .global_vars import MAX_RIDE_CAPACITY, VEHICLE_TYPE_,CHOCICE_FIELD_VEHICLE_TYPE_
import pytz

class SignupForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = MyUser
        fields = ('username', 'email')


class UserProfileEditForm(forms.Form):
    email = forms.EmailField()

    def clean_email(self):
        data = self.cleaned_data['email']
        return data


class DriverProfileEditForm(UserProfileEditForm):
    plate_num = forms.CharField(max_length=10)
    vehicle_type = forms.ChoiceField(choices=VEHICLE_TYPE_)
    capacity = forms.IntegerField(min_value=1, max_value=MAX_RIDE_CAPACITY)
    special_vehicle_info = forms.CharField(widget=forms.Textarea, required=False)
    
    def __init__(self, *args, **kwargs):
        self.vehicle = kwargs.pop('vehicle')
        self.myself = kwargs.pop('myself')
        self.current_plate_num = self.myself.plate_num.plate_num
        super(DriverProfileEditForm, self).__init__(*args, **kwargs)

    def clean_plate_num(self):
        data = self.cleaned_data['plate_num']
        if data != self.current_plate_num:
            print(self.current_plate_num)
            if self.vehicle.objects.filter(plate_num=data).exists():
                raise ValidationError(_('Invalid plate number - This plate number are in use!'))
        return data
    
    def clean_vehicle_type(self):
        data = self.cleaned_data['vehicle_type']
        return data

    def clean_capacity(self):
        data = self.cleaned_data['capacity']
        return data

    def clean_special_vehicle_info(self):
        data = self.cleaned_data['special_vehicle_info']
        return data


class RideCreationForm(forms.Form):
    dest = forms.CharField(max_length=100)
    pickup_time = forms.DateTimeField()
    owner_pass_num = forms.IntegerField(
        min_value=1, max_value=MAX_RIDE_CAPACITY)
    sharable = forms.BooleanField(required=False)
    vehicle_type = forms.ChoiceField(choices=CHOCICE_FIELD_VEHICLE_TYPE_, required=False)
    special_requests = forms.CharField(widget=forms.Textarea, required=False)
    # actual_pass_num, ride_status, owner, driver
    
    def clean_dest(self):
        data = self.cleaned_data['dest']
        return data

    def clean_pickup_time(self):
        """Remove form content if invalid input is detected"""
        data = self.cleaned_data['pickup_time']
        if data <  timezone.now() + datetime.timedelta(minutes=5):
            raise ValidationError(_(
        'Invalid pickup datetime - too early, should be set at least 5 min after!'))
        # if data > timezone.now() + datetime.timedelta(hours=12):
        #     raise ValidationError(_(
        # 'Invalid pickup datatime - too late, should be set at less than 12 hours ahead!'))

        return data

    def clean_owner_pass_num(self):
        data = self.cleaned_data['owner_pass_num']
        if data > MAX_RIDE_CAPACITY:
            raise ValidationError(_(
        'Invalid owner passenger number: should between 1 - {}'.format(MAX_INIT_RIDE_CAPACITY)))
        return data

    def clean_sharable(self):
        data = self.cleaned_data['sharable']
        return data

    def clean_vehicle_type(self):
        data = self.cleaned_data['vehicle_type']
        return data

    def clean_special_requests(self):
        data = self.cleaned_data['special_requests']
        return data


class RideEditForm(RideCreationForm):
    sharable = forms.BooleanField(required=False, disabled=True)
    def __init__(self, *args, **kwargs):
        self.ride = kwargs.pop('ride')
        self.old_pass_num = self.ride.owner_pass_num
        self.old_avail_seats = self.ride.avail_seats
        self.sharer_pass_num = self.ride.actual_pass_num - self.old_pass_num
        super(RideEditForm, self).__init__(*args, **kwargs)

    # def clean_vehicle_type(self):
    #     data = self.cleaned_data['vehicle_type']
    #     if data != "":
    #         if self.cleaned_data['owner_pass_num'] + self.sharer_pass_num > VT2CAP[data] - 1:
    #             raise ValidationError(_('Invalid vehicle type - exeed the capacity of the vehicle type'))
    #         if (self.cleaned_data['owner_pass_num'] - self.old_pass_num) > self.old_avail_seats:
    #             raise ValidationError(_('Invalid passenger number - exeed the capacity of the vehicle type'))        
    #     return data

    # def clean_owner_pass_num(self):
    #     data = self.cleaned_data['vehicle_type']
    #     if (self.cleaned_data['owner_pass_num'] - self.old_pass_num) > self.old_avail_seats:
    #         raise ValidationError(_('Invalid passenger number - exeed the capacity of the vehicle type'))
    #     return data

 


class JoinRideForm(forms.Form): 
    destination = forms.CharField(max_length=100)
    earliest_pickup_time = forms.DateTimeField()
    latest_pickup_time = forms.DateTimeField()
    number_of_passengers = forms.IntegerField(min_value=1, max_value=MAX_RIDE_CAPACITY)
    # special_requests = forms.CharField(widget=forms.Textarea, required=False)

    def clean_destination(self):
        data = self.cleaned_data['destination']
        return data

    def clean_earliest_pickup_time(self):
        """Remove form content if invalid input is detected"""
        data = self.cleaned_data['earliest_pickup_time']
        if data <  timezone.now() + datetime.timedelta(minutes=5):
            raise ValidationError(_(
        'Invalid pickup datetime - too early, should be set at least 5 min after!'))
        # if data > timezone.now() + datetime.timedelta(hours=12):
        #     raise ValidationError(_(
        # 'Invalid pickup datatime - too late, should be set at less than 12 hours ahead!'))
        return data
    

    def clean_latest_pickup_time(self):
        """Remove form content if invalid input is detected"""
        data = self.cleaned_data['latest_pickup_time']
        if data <  timezone.now() + datetime.timedelta(minutes=5):
            raise ValidationError(_(
        'Invalid pickup datetime - too early, should be set at least 5 min after!'))
        # if data > timezone.now() + datetime.timedelta(hours=12):
        #     raise ValidationError(_(
        # 'Invalid pickup datatime - too late, should be set at less than 12 hours ahead!'))
        
        # if data <= self.cleaned_data['earliest_pickup_time']:
        #     raise ValidationError(_('Invalid latest datetime - should be later than earliest datetime!'))
        edt=pytz.timezone('America/New_York')
        earliest_pickup_time= datetime.datetime.strptime(self.data['earliest_pickup_time'], '%Y-%m-%d %H:%M:%S')
        if data <= edt.localize(earliest_pickup_time):
            raise ValidationError(_('Invalid latest datetime - should be later than earliest datetime!'))
        return data

    def clean_number_of_passengers(self):
        data = self.cleaned_data['number_of_passengers']
        if data > MAX_RIDE_CAPACITY:
            raise ValidationError(_(
        'Invalid number of passengers - should between 1 - {}'.format(MAX_RIDE_CAPACITY)))
        return data

    # def clean_special_requests(self):
    #     data = self.cleaned_data['special_requests']
    #     return data


class driverRegistrationForm(forms.Form):
    plate_num = forms.CharField(max_length=20)
    vehicle_type = forms.ChoiceField(choices=VEHICLE_TYPE_)
    capacity = forms.IntegerField(min_value=1, max_value=MAX_RIDE_CAPACITY, required=True)
    special_vehicle_info = forms.CharField(widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        self.vehicle = kwargs.pop('vehicle')
        super(driverRegistrationForm, self).__init__(*args, **kwargs)

    def clean_plate_num(self):
        data = self.cleaned_data['plate_num']
        if self.vehicle.objects.filter(plate_num=data).exists():
            raise ValidationError(_('Invalid plate number - This plate number is in use!'))
        return data
    
    def clean_vehicle_type(self):
        data = self.cleaned_data['vehicle_type']
        return data
    
    def clean_capacity(self):
        data = self.cleaned_data['capacity']
        return data

    def clean_special_vehicle_info(self):
        data = self.cleaned_data['special_vehicle_info']
        return data


class sharerEdittingForm(forms.Form):
    new_passenger_number = forms.IntegerField(min_value=1, max_value=MAX_RIDE_CAPACITY)
    def __init__(self, *args, **kwargs):
        self.ride = kwargs.pop('ride')
        self.sharer = kwargs.pop('sharer')
        self.old_pass_num = self.sharer.pass_num
        super(sharerEdittingForm, self).__init__(*args, **kwargs)

    def clean_new_passenger_number(self):
        data = self.cleaned_data['new_passenger_number']
        if data - self.old_pass_num > self.ride.avail_seats:
            raise ValidationError(_('Invalid passenger number - exceed the capacity of the vehicle type!'))
        return data