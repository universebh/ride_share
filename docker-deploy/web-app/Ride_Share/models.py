# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractUser
from .global_vars import VEHICLE_TYPE_, RIDE_STATUS_

class Sharer(models.Model):
    pass_num = models.IntegerField(null=True)
    earliest_date_time = models.DateTimeField(null=True)
    latest_date_time = models.DateTimeField(null=True)
    dest = models.CharField(max_length=100, null=True)
    sharerid = models.OneToOneField('MyUser', models.DO_NOTHING, db_column='sharerid', primary_key=True)
    # rideid = models.ForeignKey(Ride, on_delete=models.SET_NULL, db_column='rideid', null=True)
    # special_requests = models.TextField(max_length=140, default='')

    class Meta:
        # managed = False
        db_table = 'sharer'


class Ride(models.Model):
    vehicle_type = models.CharField(max_length=10, choices=VEHICLE_TYPE_, null=True)
    dest = models.CharField(max_length=100)
    pickup_time = models.DateTimeField()
    owner_pass_num = models.IntegerField()
    actual_pass_num = models.IntegerField()
    ride_status = models.CharField(max_length=10, choices=RIDE_STATUS_, default='opn')
    sharable = models.BooleanField(blank=True)
    avail_seats = models.IntegerField(null=True)
    ride_id = models.AutoField(primary_key=True)
    owner = models.ForeignKey('MyUser', models.DO_NOTHING, db_column='owner', related_name='owner2id')
    share_id = models.ManyToManyField('MyUser', db_column='sharer', blank=True)
    driver = models.ForeignKey(
        'MyUser', on_delete=models.SET_NULL, 
        db_column='driver', null=True, blank=True, related_name= 'driver2id')
    special_requests = models.TextField(max_length=140, default='')

    class Meta:
        # managed = False
        db_table = 'ride'
# class Userprofile(models.Model):
#     userid = models.AutoField(primary_key=True)
#     plate_num = models.ForeignKey('Vehicle', models.DO_NOTHING, db_column='plate_num', blank=True, null=True)
#     first_name = models.CharField(max_length=30)
#     last_name = models.CharField(max_length=30)

#     class Meta:
#         managed = False
#         db_table = 'userprofile'

class RegisteredSharer(models.Model):
    registered_sharer_id = models.ForeignKey('MyUser', on_delete=models.SET_NULL, null=True)
    rideid = models.ForeignKey(Ride, on_delete=models.SET_NULL, null=True)
    pass_num = models.IntegerField(null=True)

class Vehicle(models.Model):
    type = models.CharField(max_length=10, choices=VEHICLE_TYPE_)
    plate_num = models.CharField(primary_key=True, max_length=20)
    capacity = models.IntegerField()
    special_vehicle_info = models.TextField(max_length=140, default='')

    class Meta:
        # managed = True
        db_table = 'vehicle'

class MyUser(AbstractUser):
    email = models.EmailField(_('Email address'), blank=False, help_text="Required.")
    plate_num = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, db_column='plate_num',null=True)
    # first_name = models.CharField(max_length=30)
    # last_name = models.CharField(max_length=30)
    # pass
    # class Meta:
    #     # managed = True
    #     db_table = 'myuser'