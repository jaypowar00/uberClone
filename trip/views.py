import os
import requests
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from user.decorators import check_blacklisted_token
from user.models import TripLocations
from user.serializers import TripLocationsSerializer


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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@check_blacklisted_token
def get_location_path(request):
    if not (request.data.get('from_lat') and request.data.get('from_lon')):
        return Response(
            {
                'status': False,
                'message': 'Provide current(start) location!'
            }
        )
    from_lat = request.data.get('from_lat')
    from_lon = request.data.get('from_lon')
    if request.data.get('to_trip'):
        location = TripLocations.objects.filter(id=request.data.get('to_trip')).first()
        if location is None:
            return Response(
                {
                    'status': False,
                    'message': 'Destination location does not exists!'
                }
            )
        to_lat = location.lat
        to_lon = location.lon
    elif request.data.get('to_lat') and request.data.get('to_lon'):
        to_lat = request.data.get('to_lat')
        to_lon = request.data.get('to_lon')
    else:
        return Response(
            {
                'status': False,
                'message': 'provide destination location!'
            }
        )
    querystring = {"origin": f"{from_lat},{from_lon}", "destination": f"{to_lat},{to_lon}"}

    headers = {
        "X-RapidAPI-Key": os.getenv('DIRECTION_API_KEY_HEADER', ''),
        "X-RapidAPI-Host": os.getenv('DIRECTION_API_HOST_HEADER', '')
    }

    response = requests.request("GET", os.getenv('DIRECTION_API_ENDPOINT', 'http://localhost:3000/'), headers=headers, params=querystring).json()
    response['route']['geometry']['coordinates'] = [{'lat': coordinate[0], 'lng': coordinate[1]} for coordinate in response['route']['geometry']['coordinates']]
    return Response(
        {
            'status': True,
            'route': response['route'] if response else {}
        }
    )
