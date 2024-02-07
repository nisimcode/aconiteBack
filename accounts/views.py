import os

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone
from dotenv import load_dotenv
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Profile
from .serializers import UserSerializer, MyTokenObtainPairSerializer


class MyTokenObtainPairView(TokenObtainPairView):
    """
    Custom view for obtaining a token.
    Inherits from the TokenObtainPairView class provided by the Django REST Framework.
    """

    serializer_class = MyTokenObtainPairSerializer
    """
    The serializer class to be used for obtaining a token.
    """


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def users(request):
    """
    Retrieves a list of active users.

    Args:
        request (Request): The HTTP request object.

    Returns:
        Response: The HTTP response object containing the serialized data of the active users.
    """

    # Retrieve active users from the database
    users_set = User.objects.filter(is_active=True)
    # Serialize the user data
    users_set_serialized = UserSerializer(users_set, many=True)

    # Return the serialized data as an HTTP response with 200 status code
    return Response(status=status.HTTP_200_OK, data=users_set_serialized.data)


@api_view(["POST"])
@permission_classes([AllowAny])
def signup(request):
    # new_user = User.objects.create_user(
    #     username=request.data["username"],
    #     email=request.data["email"],
    #     password=request.data["password"],
    # )

    email_data = request.data["email"]
    username_data = request.data["username"]
    password_data = request.data["password"]

    if User.objects.filter(email=email_data).exists():
        return Response(status=status.HTTP_409_CONFLICT, data={"detail": "Email already exists"})
    if User.objects.filter(username=username_data).exists():
        return Response(status=status.HTTP_409_CONFLICT, data={"detail": "Username already exists"})

    email_fine = (email_data.count("@") == 1 and "." in email_data)
    username_fine = 4 <= len(username_data) <= 16
    password_fine = 8 <= len(password_data) <= 16

    if not (username_fine and email_fine and password_fine):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    new_user = User.objects.create_user(
        username=request.data["username"],
        email=request.data["email"],
        password=request.data["password"],
        is_active=False,  # Set the user as inactive initially
    )
    user = User.objects.get(id=new_user.id)
    load_dotenv()
    welcome_homepage = os.getenv("WELCOME_HOMEPAGE")
    print(welcome_homepage)
    serializer = MyTokenObtainPairSerializer()
    token = serializer.get_token(user)
    activation_link = f"http://127.0.0.1:8000/accounts/profile/activate/?token={token}"

    # # Send text only activation email
    # subject = 'Welcome to Aconite'
    # message = f'''
    #     Thank you for signing up. Please finalize the processing by clicking the link provided.
    #     {activation_link}
    #     '''
    # recipient_list = [user.email]
    # send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)

    # Send HTML activation email
    subject = 'Welcome to Aconite'
    from_email = settings.DEFAULT_FROM_EMAIL
    to = user.email
    text_content = f'''
        Thank you for signing up. Please finalize the processing by clicking the link provided.
        {activation_link}
        '''
    html_content = f'''
        Thank you for signing up. Please finalize the processing by clicking <a href="{activation_link}">here</a>.
        '''
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

    return Response(status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([AllowAny])
def profile(request):
    if not request.user.is_authenticated:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    user = request.user
    serializer = UserSerializer(user)
    return Response(status=status.HTTP_200_OK, data=serializer.data)


@api_view(["GET", "PATCH"])
@permission_classes([AllowAny])
def activate(request, user_id=None):
    if request.GET.get('token'):
        token_data = request.GET.get('token')
        try:
            # serializer = TokenActivationSerializer(data=token_data)
            token = RefreshToken(token_data)
            username = token.payload.get('username')
            email = token.payload.get('email')
            user = User.objects.get(username=username, email=email)
            user.is_active = True  # Activate the user
            user.save()
            Profile.objects.create(user=user)
            return Response(status=status.HTTP_302_FOUND,
                            headers={'Location': os.environ.get(
                                "WELCOME_HOMEPAGE")})
        except (ObjectDoesNotExist, TokenError,) as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)

    if request.user.id == user_id:
        user = request.user
        user.is_active = True  # Activate the user
        user.save()
        return Response(status=status.HTTP_302_FOUND,
                        headers={'Location': os.environ.get(
                            "WELCOME_HOMEPAGE")})

    if request.user.is_staff:
        user = User.objects.get(id=user_id)
        user.is_active = True  # Activate the user
        user.save()
        return Response(status=status.HTTP_302_FOUND)

    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def deactivate(request):
    if request.user.id == request.data.get('user_id') or request.user.is_staff:
        user_profile = Profile.objects.get(user_id=request.data.get('user_id'))
        user_profile.deactivated_at = timezone.now()
        user_profile.is_deactivated = True
        user_profile.save()
        return Response(status=status.HTTP_204_NO_CONTENT,
                        headers={'Location': os.environ.get(
                            "WELCOME_HOMEPAGE")})

    return Response(status=status.HTTP_400_BAD_REQUEST)
