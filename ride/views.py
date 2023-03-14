import math
import os
import random
import time
from datetime import timedelta, datetime
import requests
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from uberClone.settings import idle_drivers, ride_otps
from user.decorators import check_blacklisted_token
from user.models import User, Ride


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@check_blacklisted_token
def book_ride(request):
    user = request.user
    if user.account_type == User.AccountType.DRIVER:
        return Response(
            {
                'status': False,
                'message': 'this feature is only for regular account types, not driver'
            }
        )
    jsn = request.body
    if not ('from_lat' in jsn and 'from_lng' in jsn and 'to_lat' in jsn and 'to_lng' in jsn and 'driver' in jsn):
        return Response(
            {
                'status': False,
                'message': 'missing some fields in the request body (required data: from_lat, from_lng, to_lat, to_lng)'
            }
        )
    driver_user = User.objects.filter(id=jsn['driver']).first()
    if driver_user is None:
        return Response(
            {
                'status': False,
                'message': 'provided driver account does not exists'
            }
        )
    try:
        driver = driver_user.driver
    except User.driver.RelatedObjectDoesNotExist:
        return Response(
            {
                'status': False,
                'message': 'provided driver account is not a driver account'
            }
        )
    if driver.vehicle is None:
        return Response(
            {
                'status': False,
                'message': 'provided driver account does not owns a vehicle yet'
            }
        )
    vehicle = driver.vehicle
    # getting price for customer pickup location to destination location travelling
    querystring = {"origin": f"{jsn['from_lat']},{jsn['from_lng']}", "destination": f"{jsn['to_lat']},{jsn['to_lng']}"}
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
    price = ((response['distance'] / 1000.0) * 105) / vehicle.mileage
    # getting price for driver idle location to customer pickup location travelling
    querystring = {"origin": f"{idle_drivers[f'{driver_user.id}']['lat']},{idle_drivers[f'{driver_user.id}']['lng']}",
                   "destination": f"{jsn['from_lat']},{jsn['from_lng']}"}
    response = requests.request("GET", os.getenv('DIRECTION_API_ENDPOINT', 'http://localhost:3000/'), headers=headers,
                                params=querystring).json()
    if response is None:
        return Response(
            {
                'status': False,
                'message': 'something went wrong while getting route details from start to destination locations'
            }
        )
    price += ((response['distance'] / 1000.0) * 105) / vehicle.mileage
    ride = Ride(
        user=user.id,
        driver=driver.id,
        start_destination_lat=jsn['from_lat'],
        start_destination_lng=jsn['from_lng'],
        end_destination_lat=jsn['to_lat'],
        end_destination_lng=jsn['to_lng'],
        vehicle=vehicle.id,
        price=price,
        user_history=user.id
    )
    ride.save()
    return Response(
        {
            'state': True,
            'message': 'Ride successfully booked!',
            'ride': ride.id
        }
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@check_blacklisted_token
def cancel_ride(request):
    return None


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
