# from channels.middleware import BaseMiddleware
# import jwt
# from django.contrib.auth import get_user_model
# from django.conf import settings
# from channels.db import database_sync_to_async
# from django.contrib.auth.models import AnonymousUser

# User = get_user_model()

# class JWTAuthMiddleware(BaseMiddleware):
#     async def __call__(self, scope, receive, send):

#         token = None

#         # 1. Extract token from Authorization header
#         headers = dict(scope['headers'])
#         auth_header = headers.get(b'authorization', None)
#         if auth_header:
#             # Header format: b'Token <jwt>'
#             token_str = auth_header.decode()
#             parts = token_str.split()
#             if len(parts) == 2 and parts[0].lower() == 'token':
#                 token = parts[1]

#         user = None
#         if token:
#             try:
#                 payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
#                 user_id = payload.get('user_id')
#                 if user_id:
#                     try:
#                         user = await database_sync_to_async(User.objects.get)(id=user_id)
#                     except User.DoesNotExist:
#                         user = None
#             except jwt.ExpiredSignatureError:
#                 user = None
#             except jwt.DecodeError:
#                 user = None

#         scope['user'] = user if user else AnonymousUser()

#         # Pass to the next layer
#         return await super().__call__(scope, receive, send)



# channels_middleware.py (example)
from channels.middleware import BaseMiddleware
import jwt
from django.contrib.auth import get_user_model
from django.conf import settings
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from urllib.parse import parse_qs

User = get_user_model()

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        token = None

        # 1. Try query string first (ws://.../?token=...)
        query_string = scope.get('query_string', b'').decode()
        if query_string:
            qs = parse_qs(query_string)
            token_list = qs.get('token')
            if token_list:
                token = token_list[0]

        # 2. Fallback: Authorization header (format: Token <jwt>)
        if not token:
            headers = dict(scope.get('headers', []))
            auth_header = headers.get(b'authorization', None)
            if auth_header:
                token_str = auth_header.decode()
                parts = token_str.split()
                if len(parts) == 2 and parts[0].lower() == 'token':
                    token = parts[1]

        user = None
        if token:
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                user_id = payload.get('user_id')
                if user_id:
                    try:
                        user = await database_sync_to_async(User.objects.get)(id=user_id)
                    except User.DoesNotExist:
                        user = None
            except jwt.ExpiredSignatureError:
                user = None
            except jwt.DecodeError:
                user = None

        scope['user'] = user if user else AnonymousUser()
        return await super().__call__(scope, receive, send)







'''from channels.middleware import BaseMiddleware
from urllib.parse import parse_qs
import jwt
from django.contrib.auth import get_user_model
from django.conf import settings
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser

User = get_user_model()

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):

        #1. Decode bytes to string
        query_string = scope['query_string'].decode()   # 'token=abc123'

        #2. Parse to dict
        query_params = parse_qs(query_string)   # {'token': ['abc123']}

        #3. Get the token
        token = query_params.get('token', [None])[0]   # 'abc123'

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')
        except jwt.ExpiredSignatureError:
            # token expired
            user_id = None
        except jwt.DecodeError:
            user_id = None

        if user_id:
            try:
                user = await database_sync_to_async(User.objects.get)(id=user_id)
            except User.DoesNotExist:
                user = None
        else:
            user=None
        if user:
            scope['user'] = user # authenticated user
        else:
            
            scope['user'] = AnonymousUser()
        
        # pass to the next layer
        return await super().__call__(scope, receive, send)
    
'''
"""
just liitle code then above
"""
# import jwt
# from django.conf import settings
# from channels.middleware import BaseMiddleware
# from django.contrib.auth import get_user_model
# from jwt import InvalidTokenError
# from channels.db import database_sync_to_async


# @database_sync_to_async
# def get_user(user_id):
#     User = get_user_model()

#     try:
#         return User.objects.get(id=user_id)
#     except User.DoesNotExist:
#         return None

# class JWTAuthMiddleware(BaseMiddleware):
#     async def __call__(self, scope, receive, send):
#         from rest_framework_simplejwt.tokens import UntypedToken
#         headers = dict(scope['headers'])
#         if b'authorization' in headers:
#             token_name, token = headers[b'authorization'].decode().split()
#             if token_name.lower() == 'bearer':
#                 try:
#                     payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
#                     scope['user'] = await get_user(payload['user_id'])
#                 except InvalidTokenError:
#                     scope['user'] = None
#         return await super().__call__(scope, receive, send)
