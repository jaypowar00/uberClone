from rest_framework import serializers
from user.models import Vehicle
from user.serializers import GeneralResponse


class AddVehicleRequest(serializers.Serializer):
    vehicle_no = serializers.CharField()
    seat_cap = serializers.IntegerField()
    mileage = serializers.FloatField()
    vehicle_type = serializers.ChoiceField(choices=Vehicle.Type.choices)


class VehicleDetailsRequest(serializers.Serializer):
    driver_id = serializers.IntegerField()


class VehicleGeneral(serializers.Serializer):
    id = serializers.IntegerField()
    vehicle_number = serializers.CharField()
    seat_capacity = serializers.IntegerField()
    mileage = serializers.FloatField()
    type = serializers.CharField()
class VehicleDetailsResponse(GeneralResponse):
    message = serializers.CharField(allow_null=True, required=False)
    vehicle = VehicleGeneral(allow_null=True, required=False)

class UpdateVehicleDetailsRequest(serializers.Serializer):
    vehicle_no = serializers.CharField()
    seat_cap = serializers.IntegerField()
    mileage = serializers.FloatField()
    vehicle_type = serializers.ChoiceField(choices=Vehicle.Type.choices)


class NearbyIdleDriversRequest(serializers.Serializer):
    lat = serializers.FloatField()
    lng = serializers.FloatField()
    vehicle_type = serializers.ChoiceField(choices=Vehicle.Type.choices)
    test = serializers.BooleanField(default=None, required=False, allow_null=True)


class DriverGeneralSerializer(serializers.Serializer):
    lat = serializers.FloatField()
    lng = serializers.FloatField()
    user_id = serializers.IntegerField()
    vehicle_type = serializers.ChoiceField(choices=Vehicle.Type.choices)
    vehicle_number = serializers.CharField()
    seat_capacity = serializers.IntegerField()


class NearbyIdleDriversResponse(GeneralResponse):
    message = serializers.CharField(allow_null=True, required=False)
    drivers = serializers.ListField(child=DriverGeneralSerializer(), allow_null=True, required=False)
    nearest_driver = DriverGeneralSerializer(allow_null=True, required=False)
