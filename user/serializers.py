from rest_framework import serializers
from .models import User, TripLocations, Vehicle, Ride
import geocoder


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'public_id', 'email', 'name', 'username', 'address', 'gender', 'phone', 'dob', 'account_type', 'date_joined', 'about']


class VehicleSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField('get_vehicle_type')
    class Meta:
        model = Vehicle
        fields = ['id', 'vehicle_number', 'seat_capacity', 'mileage', 'type']

    def get_vehicle_type(self, vehicle_obj):
        type_str = vehicle_obj.vehicle_type
        type_str = 'Sedan' if type_str == vehicle_obj.Type.CAR_SEDAN \
            else 'Suv' if type_str == vehicle_obj.Type.CAR_SUV \
            else 'Rikshaw' if type_str == vehicle_obj.Type.RIKSHAW \
            else 'BIKE'
        return type_str


class TripLocationsSerializer(serializers.ModelSerializer):
    geo = serializers.SerializerMethodField('get_geo_details')

    class Meta:
        model = TripLocations
        fields = ['id', 'name', 'address', 'thumbnail', 'lng', 'lat', 'description', 'geo']

    def get_geo_details(self, trip_location_obj):
        geo = geocoder.osm([trip_location_obj.lat, trip_location_obj.lng], method='reverse')
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


class RideSerializer(serializers.ModelSerializer):
    to_location = serializers.SerializerMethodField('get_to_location')
    from_location = serializers.SerializerMethodField('get_from_location')

    class Meta:
        model = Ride
        fields = ["id", "start_destination_lat", "start_destination_lng", "end_destination_lat", "end_destination_lng",
                  "from_location", "to_location", "price", "state", "otp_verified", "vehicle", "payment", "user_history",
                  "driver_history"]

    def get_to_location(self, ride):
        geo = geocoder.osm([ride.end_destination_lat, ride.end_destination_lng], method='reverse')
        print(geo.one_result.__dict__)
        return geo.address

    def get_from_location(self, ride):
        geo = geocoder.osm([ride.end_destination_lat, ride.end_destination_lng], method='reverse')
        return geo.address
