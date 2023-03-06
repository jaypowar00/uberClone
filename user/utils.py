from rest_framework.views import exception_handler

from uberClone.settings import blackListedTokens
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
