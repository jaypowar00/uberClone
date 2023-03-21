from rest_framework import serializers
from user.serializers import GeneralResponse


class GeoLocationSerializer(serializers.Serializer):
    lat = serializers.FloatField()
    lng = serializers.FloatField()


class Bounds_Route_GetLocationPath(serializers.Serializer):
    south = serializers.FloatField()
    west = serializers.FloatField()
    north = serializers.FloatField()
    east = serializers.FloatField()


class Geometry_Route_GetLocationPath(serializers.Serializer):
    coordinates = serializers.ListField(child=GeoLocationSerializer())


class Step_Route_GetLocationPath(serializers.Serializer):
    distance = serializers.FloatField()
    duration = serializers.FloatField()
    start_point_index = serializers.IntegerField()
    start_point = GeoLocationSerializer()
    end_point_index = serializers.IntegerField()
    end_point = GeoLocationSerializer()
    bounds = Bounds_Route_GetLocationPath()
    maneuver = serializers.CharField(allow_null=True, required=False)


class Route_GetLocationPath(serializers.Serializer):
    distance = serializers.IntegerField()
    duration = serializers.IntegerField()
    bounds = Bounds_Route_GetLocationPath()
    geometry = Geometry_Route_GetLocationPath()
    steps = serializers.ListField(child=Step_Route_GetLocationPath())


class GetLocationPathResponse(GeneralResponse):
    message = serializers.CharField(required=False, allow_null=True)
    route = Route_GetLocationPath(allow_null=True, required=False)


class GetLocationPathRequest(serializers.Serializer):
    from_lat = serializers.FloatField()
    from_lng = serializers.FloatField()


class Geo_Location_GetTripLocationsResponse(serializers.Serializer):
    country = serializers.CharField()
    city = serializers.CharField()
    district = serializers.CharField()
    region = serializers.CharField()
    village = serializers.CharField()
    state = serializers.CharField()
    display_address = serializers.CharField()
    postcode = serializers.CharField()
    place_id = serializers.IntegerField()
    accuracy = serializers.FloatField()


class Location_GetTripLocationsResponse(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    address = serializers.CharField()
    thumbnail = serializers.URLField()
    lat = serializers.FloatField()
    lng = serializers.FloatField()
    description = serializers.CharField()
    geo = Geo_Location_GetTripLocationsResponse()


class GetTripLocationsResponse(GeneralResponse):
    message = serializers.CharField(allow_null=True, required=False)
    locations = serializers.ListField(child=Location_GetTripLocationsResponse(), allow_null=True,
                                      required=False)