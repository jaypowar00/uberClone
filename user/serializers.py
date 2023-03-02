from rest_framework import serializers
from .models import User, TripLocations
import geocoder


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'public_id', 'email', 'name', 'username', 'address', 'gender', 'phone', 'dob', 'account_type', 'date_joined', 'about']


class TripLocationsSerializer(serializers.ModelSerializer):
    geo = serializers.SerializerMethodField('get_geo_details')

    class Meta:
        model = TripLocations
        fields = ['id', 'name', 'address', 'thumbnail', 'lon', 'lat', 'description', 'geo']

    def get_geo_details(self, trip_location_obj):
        geo = geocoder.osm([trip_location_obj.lat, trip_location_obj.lon], method='reverse')
        return {
            'country': geo.country,
            'city': geo.city,
            'district': geo.district,
            'region': geo.region,
            'village': geo.village,
            'state': geo.state,
            'display_address': geo.address,
            'postcode': geo.postal,
            'place_id': geo.place_id,
            'accuracy': geo.accuracy
        }
