from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

from common.utils import is_fired


class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        user = super().get_user(validated_token)

        if is_fired(user):
            raise AuthenticationFailed(
                "Your account has been deactivated.",
                code="user_fired",
            )

        return user
