import geopy.distance
import pandas as pd
import geopandas as gpd
from rest_framework.views import exception_handler
from uberClone.settings import blackListedTokens, idle_drivers
from datetime import datetime, timedelta
import jwt
from django.conf import settings


def generate_access_token(user):

    access_token_payload = {
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(days=1),
        'iat': datetime.utcnow()
    }
    access_token = jwt.encode(access_token_payload, settings.SECRET_KEY, algorithm='HS256').decode('utf-8')
    if access_token in blackListedTokens:
        blackListedTokens.discard(access_token)
    return access_token


def generate_refresh_token(user):
    refresh_token_payload = {
        'user.id': user.id,
        'exp': datetime.utcnow() + timedelta(days=7),
        'iat': datetime.utcnow()
    }
    refresh_token = jwt.encode(refresh_token_payload, settings.REFRESH_SECRET_KEY, algorithm='HS256').decode('utf-8')
    if refresh_token in blackListedTokens:
        blackListedTokens.discard(refresh_token)
    return refresh_token


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        if response.data['detail'] == 'Authentication credentials were not provided.' and response.data['detail'].code == 'not_authenticated':
            del response.data['detail']
            response.data['status'] = False
            response.data['message'] = 'Unauthorized access'
        elif response.data['detail'] == 'User not found' and response.data['detail'].code == 'authentication_failed':
            del response.data['detail']
            response.data['status'] = False
            response.data['message'] = 'User (for requested access token) does not exists!'
    return response


def get_nearby_drivers(lat, lng, vehicle_type):
    cust_cords = [{'lat': lat, 'lng': lng}]
    driver_cords = [v for v in idle_drivers.values()]
    print(idle_drivers)
    print(driver_cords)
    if len(idle_drivers) == 0:
        return {
            'drivers': [],
            'message': 'currently, no drivers are idle'
        }
    driver_df = pd.DataFrame(driver_cords)
    cust_df = pd.DataFrame(cust_cords)
    driver_df = driver_df[driver_df['vehicle_type'] == vehicle_type]
    driver_gdf = gpd.GeoDataFrame(driver_df, geometry=gpd.points_from_xy(driver_df['lat'], driver_df['lng']), crs="EPSG:4326")
    cust_gdf = gpd.GeoDataFrame(cust_df, geometry=gpd.points_from_xy(cust_df['lat'], cust_df['lng']), crs="EPSG:4326")
    driver_gdf_proj = driver_gdf.to_crs("EPSG:3857")
    cust_gdf_proj = cust_gdf.to_crs("EPSG:3857")
    x = cust_gdf_proj.buffer(3845.885 * 3).unary_union
    neighbours1 = driver_gdf_proj['geometry'].intersection(x)
    nearby_drivers = driver_gdf_proj[~neighbours1.is_empty]
    nearby_drivers.drop('geometry', axis=1, inplace=True)
    nearby_drivers.drop('channel_name', axis=1, inplace=True)
    distances = [geopy.distance.distance([lat, lng], [point['lat'], point['lng']]).meters for point in nearby_drivers.to_dict('records')]
    distances = {k: v for k, v in enumerate(distances)}
    distances = dict(sorted(distances.items(), key=lambda item: item[1]))
    if len(list(distances.keys())) > 0:
        return {
            'drivers': nearby_drivers.to_dict('records'),
            'nearest_driver': nearby_drivers.to_dict('records')[list(distances.keys())[0]]
        }
    return {
        'drivers': nearby_drivers.to_dict('records'),
        'nearest_driver': None
    }


def float_formatter(number, decimals=6):
    return round(number, decimals)
