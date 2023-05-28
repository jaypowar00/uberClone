import datetime
import os
import random
import uuid
import requests
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from trip.serializers import GetLocationPathRequest, GetLocationPathResponse, \
    GetTripLocationsResponse, GetNearbyFamousLocationsRequest, GetNearbyFamousLocationsResponse, GetTripPriceRequest, \
    GetTripPriceResponse, BookTripRequest, BookTripResponse, GetTripHistoryResponse, PayTripRequest
from user.decorators import check_blacklisted_token
from user.models import TripLocations, User, Driver, BookedTrip, Payment, Vehicle
from user.serializers import TripLocationsSerializer, BookedTripSerializer, GeneralResponse
from user.utils import float_formatter


@extend_schema(
    description="get famous trip locations",
    responses={
        200: OpenApiResponse(
            response=GetTripLocationsResponse
        )
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_trip_locations(request):
    locations = TripLocations.objects.all()
    serialized_locations = TripLocationsSerializer(locations, many=True).data
    return Response(
        {
            'status': True,
            'locations': serialized_locations
        }
    )


@extend_schema(
    description="get direction path from start-location to end-location",
    request=GetLocationPathRequest,
    responses={
        200: OpenApiResponse(
            response=GetLocationPathResponse
        )
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@check_blacklisted_token
def get_location_path(request):
    BASE_FARE = 50
    COST_PER_SEC = 0.1
    LOW_MILEAGE = 40
    HIGH_MILEAGE = 17
    if not (request.data.get('from_lat') and request.data.get('from_lng')):
        return Response(
            {
                'status': False,
                'message': 'Provide current(start) location!'
            }
        )
    from_lat = float_formatter(request.data.get('from_lat'))
    from_lon = float_formatter(request.data.get('from_lng'))
    if request.data.get('to_trip'):
        location = TripLocations.objects.filter(id=request.data.get('to_trip')).first()
        if location is None:
            return Response(
                {
                    'status': False,
                    'message': 'Destination location does not exists!'
                }
            )
        to_lat = float_formatter(location.lat)
        to_lng = float_formatter(location.lon)
    elif request.data.get('to_lat') and request.data.get('to_lng'):
        to_lat = float_formatter(request.data.get('to_lat'))
        to_lng = float_formatter(request.data.get('to_lng'))
    else:
        return Response(
            {
                'status': False,
                'message': 'provide destination location!'
            }
        )
    querystring = {"origin": f"{float_formatter(from_lat)},{float_formatter(from_lon)}", "destination": f"{float_formatter(to_lat)},{float_formatter(to_lng)}"}

    headers = {
        "X-RapidAPI-Key": os.getenv('DIRECTION_API_KEY_HEADER', ''),
        "X-RapidAPI-Host": os.getenv('DIRECTION_API_HOST_HEADER', '')
    }

    response = requests.request("GET", os.getenv('DIRECTION_API_ENDPOINT', 'http://localhost:3000/'), headers=headers, params=querystring).json()
    response['route']['geometry']['coordinates'] = [{'lat': float_formatter(coordinate[0]), 'lng': float_formatter(coordinate[1])} for coordinate in response['route']['geometry']['coordinates']]
    low_price = float_formatter(BASE_FARE + ((response['route']['distance'] / 1000.0) * 105) / LOW_MILEAGE + (COST_PER_SEC * response['route']['duration']), 2)
    high_price = float_formatter(BASE_FARE + ((response['route']['distance'] / 1000.0) * 105) / HIGH_MILEAGE + (COST_PER_SEC * response['route']['duration']), 2)
    return Response(
        {
            'status': True,
            'route': response['route'] if response else {},
            'low_price': low_price,
            'high_price': high_price,
            'duration': response['route']['duration']
        }
    )


@extend_schema(
    description="get nearby famous locations based on provided current lat,lng coordinates",
    request=GetNearbyFamousLocationsRequest,
    responses={
        200: OpenApiResponse(
            response=GetNearbyFamousLocationsResponse
        )
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@check_blacklisted_token
def get_nearby_famous_locations(request):
    if not (request.data.get('from_lat') and request.data.get('from_lng')):
        return Response(
            {
                'status': False,
                'message': 'Provide current(start) location!'
            }
        )
    radius = 5000 if not request.data.get('radius') else int(request.data.get('radius'))
    from_lat = float_formatter(request.data.get('from_lat'))
    from_lng = float_formatter(request.data.get('from_lng'))
    api_key = os.getenv('GEOAPIFY_API_KEY')
    querystring = {
        "filter": f"circle:{from_lng},{from_lat},{radius}",
        "bias": f"proximity:{from_lng},{from_lat}",
        "limit": "50",
        "categories": "tourism.attraction,building.historic,entertainment.water_park,entertainment.zoo,entertainment.aquarium,entertainment.planetarium,entertainment.activity_park,entertainment.theme_park,entertainment.museum,entertainment.culture",
        "conditions": "named",
        "apiKey": f"{api_key}"
    }
    url = f"{os.getenv('GEOAPIFY_API_ENDPOINT')}"
    print('[+] url:')
    print(url)
    response = requests.request("GET", url, params=querystring).json()
    if 'statusCode' in response:
        return Response(
            {
                'status': False,
                'message': f"Server issue: {response['message']}"
            }
        )
    del_keys = ['categories', 'details', 'datasource']
    for location in response['features']:
        location['properties']['osm_id'] = location['properties']['datasource']['raw']['osm_id']
        location['category'] = location['properties']['categories'][0]
        del location['type']
        del location['geometry']
        for del_key in del_keys:
            del location['properties'][del_key]
    return Response(
        {
            'status': True,
            'locations': response['features']
        }
    )


@extend_schema(
    description="book a trip for customer",
    request=BookTripRequest,
    responses={
        200: OpenApiResponse(
            response=BookTripResponse
        )
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@check_blacklisted_token
def book_trip(request):
    BASE_FARE = 10
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
    if not ('from_lat' in jsn and 'from_lng' in jsn and 'to_lat' in jsn and 'to_lng' in jsn and 'vehicle_type' in jsn and 'from_location' and 'to_location' in jsn and 'pickup_time' in jsn):
        return Response(
            {
                'status': False,
                'message': 'missing some fields in the request body (required data: from_lat, from_lng, to_lat, to_lng, vehicle_type, to_location, from_location, pickup_time)'
            }
        )

    driver_user: User = random.choice(list(User.objects.filter(for_trip=True, account_type='D', driver__vehicle__vehicle_type__iexact=jsn['vehicle_type']).all()))
    try:
        driver: Driver = driver_user.driver
    except User.driver.RelatedObjectDoesNotExist:
        return Response(
            {
                'status': False,
                'message': 'fetched driver account is not a driver account'
            }
        )
    if driver.vehicle is None:
        return Response(
            {
                'status': False,
                'message': 'fetched driver account does not owns a vehicle yet'
            }
        )
    vehicle: Vehicle = driver.vehicle
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
    # price = float_formatter(((response['route']['distance'] / 1000.0) * 105) / vehicle.mileage + (COST_PER_SEC * response['route']['duration']), 2)
    if vehicle.vehicle_type == vehicle.Type.BUS:
        price = float_formatter(((response['route']['distance'] / 1000.0) * (float(os.getenv('UC_TRIP_PER_KM', '10')) + 2)), 2)
    else:
        price = float_formatter(((response['route']['distance'] / 1000.0) * (float(os.getenv('UC_TRIP_PER_KM', '10')) + 1)), 2)
    price += BASE_FARE
    from_location = jsn['from_location'][0:251]+"..." if len(jsn['from_location']) >= 255 else jsn['from_location']
    to_location = jsn['from_location'][0:251]+"..." if len(jsn['to_location']) >= 255 else jsn['to_location']
    pickuptime = datetime.datetime.strptime(jsn["pickup_time"], "%d/%m/%Y %H:%S")
    droptime = pickuptime + datetime.timedelta(seconds=response['route']['duration'])
    trip = BookedTrip(
        start_destination_lat=float_formatter(jsn['from_lat']),
        start_destination_lng=float_formatter(jsn['from_lng']),
        end_destination_lat=float_formatter(jsn['to_lat']),
        end_destination_lng=float_formatter(jsn['to_lng']),
        from_location=from_location,
        to_location=to_location,
        vehicle=vehicle,
        price=price,
        pickup_time=pickuptime,
        drop_time=droptime,
        user_history=user,
        driver_history=driver_user
    )
    trip.save()
    trip_ser = BookedTripSerializer(trip).data
    return Response(
        {
            'status': True,
            'message': 'Trip successfully booked!',
            'trip': trip.id,
            'details': trip_ser,
        }
    )


@extend_schema(
    description="get approx. travel price based on provided from-to lat,lng coordinates",
    request=GetTripPriceRequest,
    responses={
        200: OpenApiResponse(
            response=GetTripPriceResponse
        )
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@check_blacklisted_token
def get_trip_price(request):
    BASE_FARE = 10
    COST_PER_SEC = 0.1
    jsn = request.data
    if not ('from_lat' in jsn and 'from_lng' in jsn and 'to_lat' in jsn and 'to_lng' in jsn):
        return Response(
            {
                'status': False,
                'message': 'missing some fields in the request body (required data: from_lat, from_lng, to_lat, to_lng)'
            }
        )
    car_driver_user = random.choice(list(User.objects.filter(for_trip=True, account_type='D', driver__vehicle__vehicle_type__iexact='SEDAN').all()))
    bus_driver_user = random.choice(list(User.objects.filter(for_trip=True, account_type='D', driver__vehicle__vehicle_type__iexact='BUS').all()))
    try:
        car_driver: Driver = car_driver_user.driver
    except User.driver.RelatedObjectDoesNotExist:
        return Response(
            {
                'status': False,
                'message': 'fetched car driver account is not a driver account'
            }
        )
    if car_driver.vehicle is None:
        return Response(
            {
                'status': False,
                'message': 'fetched car driver account does not owns a vehicle yet'
            }
        )
    car_vehicle = car_driver.vehicle
    try:
        bus_driver: Driver = bus_driver_user.driver
    except User.driver.RelatedObjectDoesNotExist:
        return Response(
            {
                'status': False,
                'message': 'fetched bus driver account is not a driver account'
            }
        )
    if bus_driver.vehicle is None:
        return Response(
            {
                'status': False,
                'message': 'fetched bus driver account does not owns a vehicle yet'
            }
        )
    bus_vehicle = bus_driver.vehicle
    querystring = {"origin": f"{float_formatter(jsn['from_lat'])},{float_formatter(jsn['from_lng'])}",
                   "destination": f"{float_formatter(jsn['to_lat'])},{float_formatter(jsn['to_lng'])}"}
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
    # car_price = float_formatter(((response['route']['distance'] / 1000.0) * 105) / car_vehicle.mileage + (COST_PER_SEC * response['route']['duration']), 2)
    car_price = float_formatter(((response['route']['distance'] / 1000.0) * (float(os.getenv('UC_TRIP_PER_KM', '10')) + 1)), 2)
    car_price += BASE_FARE
    # bus_price = float_formatter(((response['route']['distance'] / 1000.0) * 105) / bus_vehicle.mileage + (COST_PER_SEC * response['route']['duration']), 2)
    bus_price = float_formatter(((response['route']['distance'] / 1000.0) * (float(os.getenv('UC_TRIP_PER_KM', '10')) + 2)), 2)
    bus_price += BASE_FARE
    return Response(
        {
            'status': True,
            'car_price': car_price,
            'bus_price': bus_price
        }
    )


@extend_schema(
    description="get logged-in customer/driver trip history",
    responses={
        200: OpenApiResponse(
            response=GetTripHistoryResponse
        )
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@check_blacklisted_token
def get_trip_history(request):
    user = request.user
    if user.account_type == user.AccountType.REGULAR:
        trips = user.user_trip_history.all().order_by('-id')[:10]
        if not trips:
            return Response(
                {
                    'status': True,
                    'message': 'no history for previous trips',
                    'rides': []
                }
            )
    else:
        trips = user.driver_trip_history.all().order_by('-id')[:10]
        if not trips:
            return Response(
                {
                    'status': True,
                    'message': 'no history for previous trips',
                    'rides': []
                }
            )
    trips_serialized = BookedTripSerializer(trips, many=True).data
    return Response(
        {
            'status': True,
            'trips': trips_serialized
        }
    )


@extend_schema(
    description="do payment for a trip",
    request=PayTripRequest,
    responses={
        200: OpenApiResponse(
            response=GeneralResponse
        )
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@check_blacklisted_token
def pay_trip(request):
    user = request.user
    if user.account_type == User.AccountType.DRIVER:
        return Response(
            {
                'status': False,
                'message': 'this feature is only for regular account types, not driver'
            }
        )
    jsn = request.data
    if not ('status' in jsn and 'trip_id' in jsn):
        return Response(
            {
                'status': False,
                'message': 'missing a field in the request body (required data: status, trip_id)'
            }
        )
    trip = BookedTrip.objects.filter(id=jsn['trip_id']).first()
    if not trip:
        return Response(
            {
                'status': False,
                'message': 'the ride does not exists'
            }
        )
    if trip.payment:
        payment = trip.payment
    else:
        payment = Payment()
    payment.transaction_id = str(uuid.uuid4())
    payment.amount = trip.price
    payment.status = payment.State.SUCCESS if jsn['status'] else payment.State.FAILED
    payment.save()
    trip.payment = payment
    trip.save()
    if jsn['status']:
        return Response(
            {
                'status': True,
                'message': 'payment successful!'
            }
        )
    else:
        return Response(
            {
                'status': False,
                'message': 'payment failed!'
            }
        )

