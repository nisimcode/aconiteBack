from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import Token


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        depth = 3


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        """
        Generates a token for the given user.
        Args:
            user (User): The user for whom the token should be generated.
        Returns:
            dict: The generated token with added username and email.
        """
        # Call the parent class method to generate the token
        token = super().get_token(user)

        # Add username and email to the token
        token["username"] = user.username
        token["email"] = user.email
        token["password"] = user.password

        return token


# Serializer for token activation
class TokenActivationSerializer(serializers.Serializer):

    def activate_user(self):
        token = Token(self.validated_data['token'])
        payload_data = token.payload
        username = payload_data.get('username')
        email = payload_data.get('email')

        try:
            user = User.objects.get(username=username, email=email)
            user.is_active = True  # Activate the user
            user.save()

            return user

        except ObjectDoesNotExist:
            return None
