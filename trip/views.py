import os
import requests
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from trip.serializers import GetLocationPathRequest, GetLocationPathResponse, \
    GetTripLocationsResponse, GetNearbyFamousLocationsRequest, GetNearbyFamousLocationsResponse
from user.decorators import check_blacklisted_token
from user.models import TripLocations
from user.serializers import TripLocationsSerializer
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
        "categories": "tourism.attraction,building.historic,entertainment.water_park,entertainment.zoo,entertainment.aquarium,entertainment.planetarium,entertainment.activty_park,entertainment.theme_park,entertainment.museum,entertainment.culture",
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

