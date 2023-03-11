import copy

from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import permission_classes, api_view

from uberClone.settings import idle_drivers
from user.models import Vehicle, User
from user.decorators import check_blacklisted_token
from user.serializers import VehicleSerializer
import pandas as pd
import geopandas as gpd


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


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@check_blacklisted_token
@csrf_exempt
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


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@check_blacklisted_token
@csrf_exempt
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


@api_view(['GET'])
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
    cust_cords = [
        {'lat': jsn['lat'], 'lng': jsn['lng']}
    ]
    driver_cords = [v for v in idle_drivers.values()]
    print(idle_drivers)
    print(driver_cords)
    if len(idle_drivers) == 0:
        return Response(
            {
                'status': False,
                'drivers': [],
                'message': 'currently, no drivers are idle'
            }
        )
    driver_df = pd.DataFrame(driver_cords)
    cust_df = pd.DataFrame(cust_cords)

    driver_df = driver_df[driver_df['vehicle_type'] == jsn['vehicle_type']]

    driver_gdf = gpd.GeoDataFrame(driver_df, geometry=gpd.points_from_xy(driver_df['lat'], driver_df['lng']), crs="EPSG:4326")
    cust_gdf = gpd.GeoDataFrame(cust_df, geometry=gpd.points_from_xy(cust_df['lat'], cust_df['lng']), crs="EPSG:4326")

    driver_gdf_proj = driver_gdf.to_crs("EPSG:3857")
    cust_gdf_proj = cust_gdf.to_crs("EPSG:3857")

    x = cust_gdf_proj.buffer((3845.885 * 999.99) / 1000).unary_union
    neighbours1 = driver_gdf_proj['geometry'].intersection(x)

    nearby_drivers = driver_gdf_proj[~neighbours1.is_empty]
    nearby_drivers.drop('geometry', axis=1, inplace=True)
    return Response(
        {
            'status': True,
            'drivers': nearby_drivers.to_dict('records')
        }
    )

