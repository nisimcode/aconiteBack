import os

import httpx
from django.db import DatabaseError
from django.shortcuts import get_object_or_404
from dotenv import load_dotenv
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from accounts.models import Profile
from decorators.custom_decorator import custom_decorator
from .models import Widget
from .serializers import WidgetSerializer
from .timestamp_converter import timestamp_converter


@api_view(["POST"])
@custom_decorator
def verify_location(request):
    if not request.data.get("location"):
        return Response(status=status.HTTP_400_BAD_REQUEST)

    print("VERIFYING: ", request.data.get("location"))
    location = request.data.get("location")

    load_dotenv()
    weather_api_url = os.getenv("WEATHER_API_CURRENT_URL")
    weather_api_key = os.getenv("WEATHER_API_KEY")

    request = httpx.get(
        weather_api_url,
        params={"key": weather_api_key, "q": location},
    )
    if request.status_code == 200:
        request_data = request.json()
        location_name = request_data["location"]["name"]

        print("LOCATION: ", location_name)
        print("TYPE: ", type(location_name))

        return Response(
            status=status.HTTP_200_OK,
            data={"location_sent": location, "location_found": location_name},
        )

    return Response(
        status=status.HTTP_400_BAD_REQUEST, data={"message": "Invalid location"}
    )


@api_view(["POST"])
@custom_decorator
def add_widget(request):
    if not request.data.get("location"):
        return Response(status=status.HTTP_400_BAD_REQUEST)

    location_name = request.data.get("location")
    profile = get_object_or_404(Profile, user=request.user)

    widget = Widget.objects.filter(location=location_name, profile=profile).first()

    if widget:
        if widget.is_active:
            return Response(
                status=status.HTTP_409_CONFLICT,
                data={"message": "Active Location widget already exists"},
            )
        widget.is_active = True
        widget.save()
        return Response(
            status=status.HTTP_200_OK,
            data={"message": "Deactivated location widget reactivated"},
        )

    try:
        Widget.objects.create(location=location_name, profile=profile)

        return Response(
            status=status.HTTP_201_CREATED, data={"message": "location widget created"}
        )
    except DatabaseError:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["PATCH"])
@custom_decorator
def remove_widget(request):
    widget_id = request.data.get("id")
    widget = get_object_or_404(Widget, id=widget_id)
    print("DELETING: ", widget.location)
    widget.is_active = False
    widget.save()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
@custom_decorator
def get_weather(request):
    load_dotenv()
    weather_api_url = os.getenv("WEATHER_API_CURRENT_URL")
    weather_api_key = os.getenv("WEATHER_API_KEY")
    try:
        profile = get_object_or_404(Profile, user=request.user)
        widgets = Widget.objects.filter(profile__id=profile.id, is_active=True)
        widgets_serialized = WidgetSerializer(widgets, many=True)
        weather_data = []
        for widget in widgets_serialized.data:
            request = httpx.get(
                weather_api_url,
                params={"key": weather_api_key, "q": widget["location"]},
            )
            if request.status_code == 200:
                request_json = request.json()
                widget_data = {
                    "id": widget["id"],
                    "location": widget["location"].title(),
                    "temperature": f"{str(int(request_json['current']['temp_c']))} °C",
                    "last_updated": timestamp_converter(
                        request_json["current"]["last_updated_epoch"]
                    ),
                    "condition_text": request_json["current"]["condition"]["text"],
                    "condition_icon": request_json["current"]["condition"]["icon"],
                }
                weather_data.append(widget_data)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_200_OK, data=weather_data)
    except Exception as error:
        print(error)
        return Response(status=status.HTTP_400_BAD_REQUEST)
