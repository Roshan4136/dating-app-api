import jwt
from django.conf import settings
from channels.middleware import BaseMiddleware
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import UntypedToken
from jwt import InvalidTokenError
from channels.db import database_sync_to_async

User = get_user_model()

@database_sync_to_async
def get_user(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        headers = dict(scope['headers'])
        if b'authorization' in headers:
            token_name, token = headers[b'authorization'].decode().split()
            if token_name.lower() == 'bearer':
                try:
                    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                    scope['user'] = await get_user(payload['user_id'])
                except InvalidTokenError:
                    scope['user'] = None
        return await super().__call__(scope, receive, send)
