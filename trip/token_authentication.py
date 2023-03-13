import django.db
import jwt
from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from uberClone import settings
from user.models import User, Ride


@database_sync_to_async
def confirm_user_for_idle_driver(scope):
    try:
        token = parse_qs(scope["query_string"].decode("utf8"))["token"][0]
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user: User
        user = User.objects.filter(id=payload['user_id']).first()
        print(1)
        if user is None:
            print(2)
            return AnonymousUser(), 'user does not exists for provided token', None
        try:
            print(3)
            if user.account_type == User.AccountType.DRIVER:
                print(5)
                print(f'[+] user.id: {user.id}')
                if user.driver.vehicle:
                    vehicle = {
                        'type': user.driver.vehicle.vehicle_type,
                        'number': user.driver.vehicle.vehicle_number,
                        'seat_capacity': user.driver.vehicle.seat_capacity,
                    }
                    return user, {'message': None}, vehicle
                return user, {'message': None}, None
            print(99)
            return AnonymousUser(), "user account is not a driver account", None
        except django.db.utils.Error:
            return AnonymousUser(), "something wrong with database", None
        except IndexError or KeyError:
            return AnonymousUser(), "index/key error occurred at server side", None
    except jwt.ExpiredSignatureError:
        return AnonymousUser(), "authentication token is expired", None
    except jwt.InvalidSignatureError:
        return AnonymousUser(), "authentication token is invalid", None
    except jwt.DecodeError:
        return AnonymousUser(), "error while decoding authentication token", None
    except KeyError:
        return AnonymousUser(), "key error occurred at server side", None


@database_sync_to_async
def confirm_user_for_live_session(scope):
    try:
        token = parse_qs(scope["query_string"].decode("utf8"))["token"][0]
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user: User
        user = User.objects.filter(id=payload['user_id']).first()
        print(1)
        if user is None:
            print(2)
            return AnonymousUser(), None, "user does not exists"
        try:
            ride_id = int(scope['path'].split('/')[-2])
            print(3)
            ride = Ride.objects.filter(id=ride_id).first()
            if ride is None:
                return AnonymousUser(), None, "ride does not exists"
            ride_loc = {
                'id': ride.id,
                'loc': {
                    'from_lat': ride.start_destination_lat,
                    'from_lng': ride.start_destination_lon,
                    'to_lat': ride.end_destination_lat,
                    'to_lng': ride.end_destination_lon,
                },
                'state': ride.state
            }
            if user.account_type == User.AccountType.REGULAR:
                print(4)
                print(user.id)
                print(ride.user.id)
                if user.id == ride.user.id:
                    return user, ride_loc, None
            elif user.account_type == User.AccountType.DRIVER:
                print(5)
                print(user.id)
                print(ride.driver.id)
                if user.id == ride.driver.id:
                    return user, ride_loc, None
            print(99)
            return AnonymousUser(), None, "current user does not have access to this Ride's live-preview"
        except django.db.utils.Error:
            return AnonymousUser(), None, "something wrong happened with database"
        except IndexError or KeyError:
            return AnonymousUser(), None, "index / key error occurred at server side"
    except jwt.ExpiredSignatureError:
        return AnonymousUser(), None, "authentication token is expired"
    except jwt.InvalidSignatureError:
        return AnonymousUser(), None, "authentication token is invalid"
    except jwt.DecodeError:
        return AnonymousUser(), None, "error while decoding authentication token"
    except KeyError:
        return AnonymousUser(), None, "key error occurred at server side"


class TokenAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        print(scope)
        self.scope = scope
        if scope['path'] != '/ws/idle-driver/':
            self.scope['user'], self.scope['ride'], self.scope['error'] = await confirm_user_for_live_session(self.scope)
        else:
            self.scope['user'], self.scope['error'], self.scope['vehicle'] = await confirm_user_for_idle_driver(self.scope)
        return await self.app(scope, receive, send)
