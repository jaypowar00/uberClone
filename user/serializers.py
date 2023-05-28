from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers
from .models import User, TripLocations, Vehicle, Ride, Payment, BookedTrip
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
            else 'Bus' if type_str == vehicle_obj.Type.BUS \
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


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['transaction_id', 'amount', 'date', 'status']


class RideSerializer(serializers.ModelSerializer):
    vehicle = VehicleSerializer()
    payment = PaymentSerializer()
    class Meta:
        model = Ride
        fields = ["id", "start_destination_lat", "start_destination_lng", "end_destination_lat", "end_destination_lng",
                  "from_location", "to_location", "price", "state", "otp_verified", "vehicle", "payment", "user_history",
                  "driver_history", "created_at", ]


class BookedTripSerializer(serializers.ModelSerializer):
    vehicle = VehicleSerializer()
    payment = PaymentSerializer()
    class Meta:
        model = BookedTrip
        fields = ["id", "start_destination_lat", "start_destination_lng", "end_destination_lat", "end_destination_lng",
                  "from_location", "to_location", "pickup_time", "drop_time", "price", "state", "vehicle", "payment",
                  "user_history", "driver_history"]


class UserGeneralSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    public_id = serializers.UUIDField()
    email = serializers.EmailField()
    name = serializers.CharField()
    username = serializers.CharField()
    address = serializers.CharField(allow_null=True, allow_blank=True)
    gender = serializers.CharField()
    phone = serializers.CharField(allow_null=True, allow_blank=True)
    dob = serializers.DateField(allow_null=True)
    account_type = serializers.ChoiceField(choices=User.AccountType.choices)
    date_joined = serializers.DateTimeField()
    about = serializers.CharField()


class GeneralResponse(serializers.Serializer):
    status = serializers.BooleanField()
    message = serializers.CharField()


@extend_schema_serializer(exclude_fields=['id'])
class User_UserProfileResponse(UserGeneralSerializer):
    pass


class UserProfileResponse(GeneralResponse):
    user = User_UserProfileResponse(allow_null=True, required=False)


class UserRegisterRequest(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    name = serializers.CharField(max_length=150)
    gender = serializers.ChoiceField(choices=User.Gender.choices)
    phone = serializers.CharField(max_length=20)
    address = serializers.CharField(max_length=200)
    account_type = serializers.ChoiceField(choices=User.AccountType.choices)


class Context_UserRegisterResponse(serializers.Serializer):
    email = serializers.EmailField()
    name = serializers.CharField()
    gender = serializers.CharField()
    phone = serializers.CharField()
    address = serializers.CharField()
    account_type = serializers.ChoiceField(choices=User.AccountType.choices)


class UserRegisterResponse(GeneralResponse):
    context = Context_UserRegisterResponse(allow_null=True, required=False)


class UserLoginRequest(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class UserLoginResponse(GeneralResponse):
    access_token = serializers.CharField(allow_null=True, required=False)
    refresh_token = serializers.CharField(allow_null=True, required=False)
    csrf_token = serializers.CharField(allow_null=True, required=False)
    user = UserGeneralSerializer(allow_null=True, required=False)


class RefreshTokenResponse(GeneralResponse):
    access_token = serializers.CharField(required=False, allow_null=True)


class UserUpdateRequest(serializers.Serializer):
    email = serializers.EmailField(required=False)
    name = serializers.CharField(required=False)
    username = serializers.CharField(required=False)
    dob = serializers.DateField(required=False)
    about = serializers.CharField(required=False)
    gender = serializers.CharField(required=False)
    phone = serializers.CharField(required=False)
    address = serializers.CharField(required=False)


class UserUpdateResponse(GeneralResponse):
    context = UserUpdateRequest(required=False, allow_null=True)


class UserUpdatePasswordRequest(serializers.Serializer):
    new_password = serializers.CharField()
    old_password = serializers.CharField()


class UserForgetPasswordRequest(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()
    skey = serializers.CharField()
