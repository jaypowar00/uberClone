import django.db
import jwt
from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from uberClone import settings
from user.models import User, Ride


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
            return AnonymousUser(), None
        try:
            ride_id = int(scope['path'].split('/')[-2])
            print(3)
            ride = Ride.objects.filter(id=ride_id).first()
            if ride is None:
                return AnonymousUser(), None
            ride_loc = {
                'id': ride.id,
                'loc': {
                    'from_lat': ride.start_destination_lat,
                    'from_lon': ride.start_destination_lon,
                    'to_lat': ride.end_destination_lat,
                    'to_lon': ride.end_destination_lon,
                },
                'state': ride.state
            }
            if user.account_type == User.AccountType.REGULAR:
                print(4)
                print(user.id)
                print(ride.user.id)
                if user.id == ride.user.id:
                    return user, ride_loc
            elif user.account_type == User.AccountType.DRIVER:
                print(5)
                print(user.id)
                print(ride.driver.id)
                if user.id == ride.driver.id:
                    return user, ride_loc
            print(99)
            return AnonymousUser(), None
        except django.db.utils.Error:
            return AnonymousUser(), None
        except IndexError or KeyError:
            return AnonymousUser(), None
    except jwt.ExpiredSignatureError or jwt.InvalidSignatureError or jwt.DecodeError:
        return AnonymousUser(), None
    except KeyError:
        return AnonymousUser(), None


class TokenAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        print(scope)
        self.scope = scope
        self.scope['user'], self.scope['ride'] = await confirm_user_for_live_session(self.scope)
        return await self.app(scope, receive, send)
