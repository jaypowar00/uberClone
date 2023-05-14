import math
import random
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes, api_view
from driver.serializers import AddVehicleRequest, VehicleDetailsRequest, \
    UpdateVehicleDetailsRequest, NearbyIdleDriversRequest, NearbyIdleDriversResponse, \
    VehicleDetailsResponse
from uberClone.settings import idle_drivers, cancelled_ride
from user.models import Vehicle, User, Ride
from user.decorators import check_blacklisted_token
from user.serializers import VehicleSerializer, GeneralResponse
from user.utils import get_nearby_drivers, float_formatter


@extend_schema(
    description="add vehicle for logged-in driver",
    request=AddVehicleRequest,
    responses={
        200: OpenApiResponse(
            response=GeneralResponse
        )
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@check_blacklisted_token
def add_vehicle(request):
    try:
        driver = request.user.driver
    except User.driver.RelatedObjectDoesNotExist:
        return Response(
            {
                'status': False,
                'message': 'only driver accounts can use this feature'
            }
        )
    if driver.vehicle is None:
        jsn = request.data
        if not ('vehicle_no' in jsn and 'seat_cap' in jsn and 'mileage' in jsn and 'vehicle_type' in jsn):
            return Response(
                {
                    'status': False,
                    'message': 'failed to add vehicle. (required data: vehicle_no, seat_cap, mileage, vehicle_type)'
                }
            )
        vehicle = Vehicle(
            vehicle_number=jsn['vehicle_no'],
            seat_capacity=jsn['seat_cap'],
            mileage=jsn['mileage'],
            vehicle_type=jsn['vehicle_type']
        )
        vehicle.save()
        driver.vehicle = vehicle
        driver.save()

        return Response(
            {
                'status': True,
                'message': f'vehicle added for driver ({request.user.email})'
            }
        )
    return Response(
        {
            'status': False,
            'message': 'driver already has a vehicle, try updating existing vehicle info instead'
        }
    )


@extend_schema(
    description="get vehicle details fpr provided driver_id",
    request=VehicleDetailsRequest,
    responses={
        200: OpenApiResponse(
            response=VehicleDetailsResponse
        )
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@check_blacklisted_token
def vehicle_details(request):
    jsn = request.data
    if 'driver_id' not in jsn:
        return Response(
            {
                'status': False,
                'message': 'missing driver_id in request'
            }
        )
    user = User.objects.filter(public_id=jsn['driver_id']).first()
    if user is None:
        return Response(
            {
                'status': False,
                'message': 'user does not exist'
            }
        )
    try:
        if user.driver.vehicle is None:
            return Response(
                {
                    'status': False,
                    'message': 'driver does not have any vehicle details'
                }
            )
        vehicle_ser = VehicleSerializer(user.driver.vehicle).data
        return Response(
            {
                'status': True,
                'vehicle': vehicle_ser
            }
        )
    except User.driver.RelatedObjectDoesNotExist:
        return Response(
            {
                'status': False,
                'message': 'driver for provided driver_id does not exist'
            }
        )


@extend_schema(
    description="update vehicle details for logged-in driver",
    request=UpdateVehicleDetailsRequest,
    responses={
        200: OpenApiResponse(
            response=GeneralResponse
        )
    }
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@check_blacklisted_token
def update_vehicle(request):
    try:
        driver = request.user.driver
        if driver.vehicle is None:
            return Response(
                {
                    'status': False,
                    'message': 'driver does not have any vehicle details to perform an update'
                }
            )
        vehicle = driver.vehicle
        vehicle_fields = ['vehicle_no', 'seat_cap', 'mileage', 'vehicle_type']
        jsn = request.data
        if len(jsn) == 0 or not(True in [key in vehicle_fields for key in jsn.keys()]):
            return Response(
                {
                    'status': False,
                    'message': 'provide at least one of the following to update vehicle detail (vehicle_no, seat_cap, mileage, vehicle_type)'
                }
            )
        vehicle.vehicle_number = jsn['vehicle_no'] if 'vehicle_no' in jsn else vehicle.vehicle_number
        vehicle.seat_capacity = jsn['seat_cap'] if 'seat_cap' in jsn else vehicle.seat_capacity
        vehicle.mileage = jsn['mileage'] if 'mileage' in jsn else vehicle.mileage
        vehicle.vehicle_type = jsn['vehicle_type'] if 'vehicle_type' in jsn else vehicle.vehicle_type
        vehicle.save()
        return Response(
            {
                'status': True,
                'message': 'vehicle details updated'
            }
        )
    except User.driver.RelatedObjectDoesNotExist:
        return Response(
            {
                'status': False,
                'message': 'this feature is only for driver user'
            }
        )


@extend_schema(
    description="delete logged-in driver's vehicle info",
    responses={
        200: OpenApiResponse(
            response=GeneralResponse
        )
    }
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@check_blacklisted_token
def delete_vehicle(request):
    try:
        driver = request.user.driver
        if driver.vehicle is None:
            return Response(
                {
                    'status': False,
                    'message': 'driver does not have any vehicle details to perform an update'
                }
            )
        driver.vehicle.delete()
        return Response(
            {
                'status': True,
                'message': 'vehicle details deleted'
            }
        )
    except User.driver.RelatedObjectDoesNotExist:
        return Response(
            {
                'status': False,
                'message': 'this feature is only for driver user'
            }
        )


@extend_schema(
    description="search nearby idle drivers from given location geo coordinates",
    request=NearbyIdleDriversRequest,
    responses={
        200: OpenApiResponse(
            response=NearbyIdleDriversResponse
        )
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@check_blacklisted_token
def search_nearby_drivers(request):
    jsn = request.data
    if not ('lat' in jsn and 'lng' in jsn and 'vehicle_type' in jsn):
        return Response(
            {
                'status': False,
                'message': 'missing some parameters in request (required data: lat, lng, vehicle_type)'
            }
        )
    if 'test' in jsn and jsn['test']:
        drivers = User.objects.filter(account_type=User.AccountType.DRIVER,
                                      driver__vehicle__vehicle_type__iexact=jsn['vehicle_type'])[:2]
        for driver_user in drivers:
            digits = "0123456789"
            if driver_user.driver.vehicle is None:
                number = ''.join([digits[math.floor(random.random() * 10)] for _ in range(4)])
                new_vehicle = Vehicle(
                    vehicle_number=f"MH 09 {number}",
                    seat_capacity=4,
                    mileage=random.randint(19, 22),
                    vehicle_type=jsn['vehicle_type']
                )
                new_vehicle.save()
                driver_user.driver.vehicle = new_vehicle
                driver_user.driver.save()
            ride = Ride.objects.filter(driver=driver_user.id).first()
            if ride:
                if ride.state not in [Ride.State.CANCELLED, Ride.State.FINISHED]:
                    cancelled_ride[f'{ride.id}'] = True
                ride.state = Ride.State.CANCELLED
                ride.user = None
                ride.driver = None
                ride.save()
            loc = {
                'lat': float_formatter(jsn['lat']+(float_formatter(random.uniform(0.004, 0.009377)) * random.choice([1, -1]))),
                'lng': float_formatter(jsn['lng']+(float_formatter(random.uniform(0.004, 0.005)) * random.choice([1, -1]))),
                'user_id': driver_user.id,
                'vehicle_type': driver_user.driver.vehicle.vehicle_type,
                'vehicle_number': driver_user.driver.vehicle.vehicle_number,
                'seat_capacity': driver_user.driver.vehicle.seat_capacity,
                'channel_name': False
            }
            idle_drivers[f'{driver_user.id}'] = loc
    res = get_nearby_drivers(float_formatter(jsn['lat']), float_formatter(jsn['lng']), jsn['vehicle_type'])
    if len(res["drivers"]) == 0:
        return Response(
            {
                'status': False,
                'drivers': [],
                'message': 'currently, no drivers are idle'
            }
        )
    return Response(
        {
            'status': True,
            'drivers': res['drivers'],
            'nearest_driver': res['nearest_driver'],
            'message': 'drivers fetched'
        }
    )


