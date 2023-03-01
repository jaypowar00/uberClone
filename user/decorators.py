from uberClone.settings import blackListedTokens
from rest_framework.response import Response


def check_blacklisted_token(function):
    def wrap(request, *args, **kwargs):
        authorization_header = request.headers.get('Authorization')
        if authorization_header:
            try:
                access_token = authorization_header.split(' ')[1]
                if access_token in blackListedTokens:
                    return Response({
                        'message': 'Misuse of deactivated token is not allowed!',
                        'status': False
                    })
            except IndexError:
                pass
        if request.method == 'POST':
            refresh_token = request.COOKIES.get('refreshtoken')
            if refresh_token in blackListedTokens:
                return Response({
                    'message': 'Misuse of deactivated token is not allowed!',
                    'status': False
                })
        return function(request, *args, **kwargs)
    return wrap
