from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers
from user.models import Ride, Vehicle
from user.serializers import GeneralResponse


class RideGeneralSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    start_destination_lat = serializers.FloatField()
    start_destination_lng = serializers.FloatField()
    end_destination_lat = serializers.FloatField()
    end_destination_lng = serializers.FloatField()
    from_location = serializers.CharField()
    to_location = serializers.CharField()
    price = serializers.FloatField()
    state = serializers.ChoiceField(choices=Ride.State.choices)
    otp_verified = serializers.BooleanField()
    vehicle = serializers.IntegerField()
    payment = serializers.IntegerField(allow_null=True, required=False)


class UserRideResponse(GeneralResponse, RideGeneralSerializer):
    message = serializers.CharField(required=False, allow_null=True)


class BookRideRequest(serializers.Serializer):
    from_lat = serializers.FloatField()
    from_lng = serializers.FloatField()
    to_lat = serializers.FloatField()
    to_lng = serializers.FloatField()
    vehicle_type = serializers.ChoiceField(choices=Vehicle.Type.choices)


class BookRideResponse(GeneralResponse):
    ride = RideGeneralSerializer()


class CancleRideRequest(serializers.Serializer):
    ride_id = serializers.IntegerField()


class GenerateRideOTPRequest(serializers.Serializer):
    ride_id = serializers.IntegerField()


class GenerateRideOTPResponse(GeneralResponse):
    message = serializers.CharField(allow_null=True, required=False)
    otp = serializers.CharField(allow_null=True, required=False)


class VerifyRideOTPRequest(serializers.Serializer):
    otp = serializers.CharField()
    ride_id = serializers.IntegerField()


class GetRideHistoryResponse(GeneralResponse):
    message = serializers.CharField(allow_null=True, required=False)
    rides = serializers.ListField(child=RideGeneralSerializer())


class PayRideRequest(serializers.Serializer):
    status = serializers.BooleanField()
    ride_id = serializers.IntegerField()
