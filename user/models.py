import uuid
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from user.managers import UserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser


class User(AbstractBaseUser, PermissionsMixin):

    class AccountType(models.TextChoices):
        REGULAR = 'R', 'Regular'
        DRIVER = 'D', 'Driver'

    class Gender(models.TextChoices):
        MALE = 'M', 'Male'
        FEMALE = 'F', 'Female'

    public_id = models.UUIDField(default=uuid.uuid4, unique=True)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=150)
    username = models.CharField(unique=True, max_length=80, default="")
    phone = models.CharField(max_length=20, default=None, null=True, blank=True, unique=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=Gender.choices)
    account_type = models.CharField(max_length=1, choices=AccountType.choices, default=AccountType.REGULAR)
    about = models.TextField(null=True, default=None, blank=True)
    date_joined = models.DateTimeField(default=timezone.now)
    is_staff = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def __str__(self):
        return self.email


class Regular(models.Model):
    id = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)


class Vehicle(models.Model):

    class Type(models.TextChoices):
        BIKE = 'BIKE', 'Bike'
        CAR_SEDAN = 'SEDAN', 'Car_Sedan'
        CAR_SUV = 'SUV', 'Car_Suv'
        RIKSHAW = 'RIK', 'Rikshaw'

    vehicle_number = models.CharField(max_length=50)
    seat_capacity = models.IntegerField(null=True, default=None)
    mileage = models.FloatField(null=True, default=None)
    vehicle_type = models.CharField(max_length=5, choices=Type.choices, default=Type.CAR_SEDAN, null=True)


class Rating(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='from_user')
    to_driver = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='to_driver')
    date = models.DateTimeField(default=timezone.now)
    rate = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(5.0)])
    comment = models.CharField(max_length=500, blank=True, null=True)


class Driver(models.Model):
    id = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    driver_license = models.CharField(max_length=50, blank=True, null=True)
    vehicle = models.OneToOneField(Vehicle, on_delete=models.SET_NULL, null=True, default=None)


class Payment(models.Model):
    class State(models.TextChoices):
        SUCCESS = 's', 'success'
        FAILED = 'f', 'failed'
    transaction_id = models.CharField(max_length=256)
    amount = models.FloatField()
    date = models.DateField()
    status = models.CharField(max_length=1, choices=State.choices)


class TripLocations(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=128)
    thumbnail = models.URLField()
    description = models.CharField(max_length=128)
    lng = models.FloatField(null=True)
    lat = models.FloatField(null=True)
    # objects = models.GeoManager()


class Ride(models.Model):

    class State(models.TextChoices):
        STARTED = 's', 'started'
        DRIVER_INCOMING = 'i', 'driver incoming'
        PICKUP_READY = 'p', 'pickup ready'
        ONGOING = 'o', 'ongoing'
        FINISHED = 'f', 'finished'
        CANCELLED = 'c', 'cancelled'

    user = models.OneToOneField(User, on_delete=models.DO_NOTHING, related_name='user_ride', null=True)
    driver = models.OneToOneField(User, on_delete=models.DO_NOTHING, related_name='driver_ride', null=True)
    start_destination_lat = models.FloatField(default=None, null=True)
    start_destination_lng = models.FloatField(default=None, null=True)
    end_destination_lat = models.FloatField(default=None, null=True)
    end_destination_lng = models.FloatField(default=None, null=True)
    vehicle = models.OneToOneField(Vehicle, on_delete=models.DO_NOTHING)
    price = models.FloatField()
    state = models.CharField(max_length=1, choices=State.choices, default=State.STARTED)
    otp_verified = models.BooleanField(default=False)
    payment = models.OneToOneField(Payment, on_delete=models.DO_NOTHING, null=True, default=None)
    user_history = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='user_ride_history', null=True, default=None)
    driver_history = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='driver_ride_history', null=True, default=None)
    # booked_by = models.OneToOneField(User, on_delete=models.DO_NOTHING)
