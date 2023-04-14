import math
import os
import random
import uuid
from datetime import timedelta, datetime
import requests
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from ride.serializers import UserRideResponse, BookRideRequest, BookRideResponse, \
    CancleRideRequest, GenerateRideOTPRequest, GenerateRideOTPResponse, \
    VerifyRideOTPRequest, GetRideHistoryResponse, PayRideRequest
from uberClone.settings import idle_drivers, ride_otps, cancelled_ride
from user.decorators import check_blacklisted_token
from user.models import User, Ride, Payment
from user.serializers import RideSerializer, GeneralResponse
from django.db.models import Q
from user.utils import get_nearby_drivers, float_formatter


@extend_schema(
    description="book a ride for customer",
    request=BookRideRequest,
    responses={
        200: OpenApiResponse(
            response=BookRideResponse
        )
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@check_blacklisted_token
def book_ride(request):
    BASE_FARE = 50
    COST_PER_SEC = 0.1
    user = request.user
    if user.account_type == User.AccountType.DRIVER:
        return Response(
            {
                'status': False,
                'message': 'this feature is only for regular account types, not driver'
            }
        )
    jsn = request.data
    if not ('from_lat' in jsn and 'from_lng' in jsn and 'to_lat' in jsn and 'to_lng' in jsn and 'vehicle_type' in jsn):
        return Response(
            {
                'status': False,
                'message': 'missing some fields in the request body (required data: from_lat, from_lng, to_lat, to_lng, vehicle_type)'
            }
        )
    while True:
        res = get_nearby_drivers(float_formatter(jsn['from_lat']), float_formatter(jsn['from_lng']), jsn['vehicle_type'])
        if len(res['drivers']) == 0:
            return Response(
                {
                    'status': False,
                    'message': 'can not book a ride, there are zero drivers nearby for given vehicle_type'
                }
            )
        if res['nearest_driver'] is None:
            return Response(
                {
                    'status': False,
                    'message': 'can not book a ride, there are no drivers nearby for given vehicle_type'
                }
            )
        nearest_driver = res['nearest_driver']
        driver_user = User.objects.filter(id=nearest_driver['user_id']).first()
        if driver_user is None:
            return Response(
                {
                    'status': False,
                    'message': 'fetched driver account does not exists'
                }
            )
        try:
            driver = driver_user.driver
        except User.driver.RelatedObjectDoesNotExist:
            return Response(
                {
                    'status': False,
                    'message': 'fetched driver account is not a driver account'
                }
            )
        if f'{driver_user.id}' not in idle_drivers:
            continue
        if driver.vehicle is None:
            return Response(
                {
                    'status': False,
                    'message': 'fetched driver account does not owns a vehicle yet'
                }
            )
        vehicle = driver.vehicle
        # getting price for customer pickup location to destination location travelling
        querystring = {"origin": f"{float_formatter(jsn['from_lat'])},{float_formatter(jsn['from_lng'])}", "destination": f"{float_formatter(jsn['to_lat'])},{float_formatter(jsn['to_lng'])}"}
        headers = {
            "X-RapidAPI-Key": os.getenv('DIRECTION_API_KEY_HEADER', ''),
            "X-RapidAPI-Host": os.getenv('DIRECTION_API_HOST_HEADER', '')
        }
        response = requests.request("GET", os.getenv('DIRECTION_API_ENDPOINT', 'http://localhost:3000/'), headers=headers,
                                    params=querystring).json()
        if response is None:
            return Response(
                {
                    'status': False,
                    'message': 'something went wrong while getting route details from start to destination locations'
                }
            )
        price = ((response['route']['distance'] / 1000.0) * 105) / vehicle.mileage + (COST_PER_SEC * response['route']['duration'])
        # getting price for driver idle location to customer pickup location travelling
        querystring = {"origin": f"{float_formatter(idle_drivers[f'{driver_user.id}']['lat'])},{float_formatter(idle_drivers[f'{driver_user.id}']['lng'])}",
                       "destination": f"{float_formatter(jsn['from_lat'])},{float_formatter(jsn['from_lng'])}"}
        response = requests.request("GET", os.getenv('DIRECTION_API_ENDPOINT', 'http://localhost:3000/'), headers=headers,
                                    params=querystring).json()
        if response is None:
            return Response(
                {
                    'status': False,
                    'message': 'something went wrong while getting route details from start to destination locations'
                }
            )
        price += float_formatter(BASE_FARE + ((response['route']['distance'] / 1000.0) * 105) / vehicle.mileage + (COST_PER_SEC * response['route']['duration']), 2)
        ride = Ride(
            user=user,
            driver=driver_user,
            start_destination_lat=float_formatter(jsn['from_lat']),
            start_destination_lng=float_formatter(jsn['from_lng']),
            end_destination_lat=float_formatter(jsn['to_lat']),
            end_destination_lng=float_formatter(jsn['to_lng']),
            vehicle=vehicle,
            price=price,
            user_history=user,
            driver_history=driver_user
        )
        try:
            ride.save()
        except IntegrityError as err:
            print(err)
            ongoing_ride_for = str(err)[str(err).find(':  Key (')+8:str(err).find('_id)=(')]
            print('[+] ongoing_ride_for:')
            print(ongoing_ride_for)
            if ongoing_ride_for == 'user':
                return Response(
                    {
                        'status': False,
                        'message': 'current user already has an ongoing ride, please cancel previous ride to start a new one!',
                        'ride': Ride.objects.filter(user=user).first()
                    }
                )
            if idle_drivers[f'{driver_user.id}']['channel_name']:
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.send)(
                    idle_drivers[f'{driver_user.id}']['channel_name'],
                    {'type': 'driver_ride_ongoing'}
                )
            del idle_drivers[f'{driver_user.id}']
            continue
        if idle_drivers[f'{driver_user.id}']['channel_name']:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.send)(
                idle_drivers[f'{driver_user.id}']['channel_name'],
                {
                    'type': 'driver_selected',
                    'ride_id': ride.id
                }
            )
        return Response(
            {
                'status': True,
                'message': 'Ride successfully booked!',
                'ride': ride
            }
        )


@extend_schema(
    description="cancel a customer ride",
    request=CancleRideRequest,
    responses={
        200: OpenApiResponse(
            response=GeneralResponse
        )
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@check_blacklisted_token
def cancel_ride(request):
    if request.user.account_type == request.user.AccountType.DRIVER:
        return Response(
            {
                'status': False,
                'message': 'only customer can cancel a ride'
            }
        )
    jsn = request.data
    if 'ride_id' not in jsn:
        return Response(
            {
                'status': False,
                'message': 'missing ride_id in request parameter'
            }
        )
    ride = Ride.objects.filter(id=jsn['ride_id']).first()
    if ride is None:
        return Response(
            {
                'status': False,
                'message': 'ride for provided ride_id does not exists'
            }
        )
    ride.state = Ride.State.CANCELLED
    ride.user = None
    ride.driver = None
    ride.save()
    cancelled_ride[f'{jsn["ride_id"]}'] = True
    return Response(
        {
            'status': True,
            'message': 'ride has been cancelled'
        }
    )


@extend_schema(
    description="generate customer otp for a PICKUP_READY ride",
    request=GenerateRideOTPRequest,
    responses={
        200: OpenApiResponse(
            response=GenerateRideOTPResponse
        )
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@check_blacklisted_token
def generate_otp(request):
    if request.user.account_type == request.user.AccountType.DRIVER:
        return Response(
            {
                'status': False,
                'message': 'only regular user can generate a new otp'
            }
        )
    jsn = request.body
    if 'ride_id' not in jsn:
        return Response(
            {
                'status': False,
                'message': 'Missing ride_id in request'
            }
        )
    ride = Ride.obejcts.filter(id=jsn['ride_id']).first()
    if ride is None:
        return Response(
            {
                'status': False,
                'message': 'ride for provided ride_id does not exists'
            }
        )
    digits = "0123456789"
    otp = ''.join([digits[math.floor(random.random() * 10)] for _ in range(4)])
    otp_expires = datetime.utcnow() + timedelta(minutes=3)
    ride_otps[f'{ride.id}'] = {'otp': otp, 'expires': otp_expires}
    return Response(
        {
            'status': True,
            'otp': f'{otp}'
        }
    )


@extend_schema(
    description="verify customers otp at driver side",
    request=VerifyRideOTPRequest,
    responses={
        200: OpenApiResponse(
            response=GeneralResponse
        )
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@check_blacklisted_token
def verify_otp(request):
    if request.user.account_type == request.user.AccountType.REGULAR:
        return Response(
            {
                'status': False,
                'message': 'otp can be only verified by driver account'
            }
        )
    jsn = request.body
    if not ('otp' in jsn and 'ride_id' in jsn):
        return Response(
            {
                'status': False,
                'message': 'missing some parameters in the request (required data: ride_id, otp)'
            }
        )
    ride = Ride.obejcts.filter(id=jsn['ride_id']).first()
    if ride is None:
        return Response(
            {
                'status': False,
                'message': 'ride for provided ride_id does not exists'
            }
        )
    current_time = datetime.utcnow()
    if f'{ride.id}' not in ride_otps:
        return Response(
            {
                'status': False,
                'message': 'otp is not generated for this ride yet'
            }
        )
    if current_time > ride_otps[f'{ride.id}']['expires']:
        return Response(
            {
                'status': False,
                'message': 'otp is expired'
            }
        )
    if ride_otps[f'{ride.id}'] != jsn['otp']:
        return Response(
            {
                'status': False,
                'message': 'incorrect otp'
            }
        )
    ride.otp_verified = True
    ride.save()
    return Response(
        {
            'status': True,
            'message': 'otp verified'
        }
    )


@extend_schema(
    description="get logged-in customer/driver ride history which are not in 'STARTED' state",
    responses={
        200: OpenApiResponse(
            response=GetRideHistoryResponse
        )
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@check_blacklisted_token
def get_ride_history(request):
    user = request.user
    if user.account_type == user.AccountType.REGULAR:
        rides = user.user_ride_history.filter(~Q(state=Ride.State.STARTED))
        if not rides:
            return Response(
                {
                    'status': True,
                    'message': 'no history for previous rides',
                    'rides': []
                }
            )
    else:
        rides = user.driver_ride_history.filter(~Q(state=Ride.State.STARTED))
        if not rides:
            return Response(
                {
                    'status': True,
                    'message': 'no history for previous rides',
                    'rides': []
                }
            )
    rides_serialized = RideSerializer(rides, many=True).data
    return Response(
        {
            'status': True,
            'rides': rides_serialized
        }
    )


@extend_schema(
    description="get logged-in Customer/Driver current ongoing ride details",
    responses={
        200: OpenApiResponse(
            response=UserRideResponse
        )
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@check_blacklisted_token
def get_ride(request):
    user = request.user
    if user.account_type == user.AccountType.REGULAR:
        try:
            ride = user.user_ride
        except ObjectDoesNotExist:
            return Response(
                {
                    'status': True,
                    'message': 'there is no on-going ride',
                    'ride': None
                }
            )
    else:
        try:
            ride = user.driver_ride
        except ObjectDoesNotExist:
            return Response(
                {
                    'status': True,
                    'message': 'there is no on-going ride',
                    'ride': None
                }
            )
    ride_ser = RideSerializer(ride).data
    return Response(
        {
            'status': True,
            'ride': ride_ser
        }
    )


@extend_schema(
    description="do payment for a ride",
    request=PayRideRequest,
    responses={
        200: OpenApiResponse(
            response=GeneralResponse
        )
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@check_blacklisted_token
def pay_ride(request):
    user = request.user
    if user.account_type == User.AccountType.DRIVER:
        return Response(
            {
                'status': False,
                'message': 'this feature is only for regular account types, not driver'
            }
        )
    jsn = request.data
    if not ('status' in jsn and 'ride_id' in jsn):
        return Response(
            {
                'status': False,
                'message': 'missing a field in the request body (required data: status, ride_id)'
            }
        )
    ride = Ride.objects.filter(id=jsn['ride_id']).first()
    if not ride:
        return Response(
            {
                'status': False,
                'message': 'the ride does not exists'
            }
        )
    if ride.payment:
        payment = ride.payment
    else:
        payment = Payment()
    payment.transaction_id = str(uuid.uuid4())
    payment.amount = ride.price
    payment.status = payment.State.SUCCESS if jsn['status'] else payment.State.FAILED
    payment.save()
    ride.payment = payment
    ride.save()
