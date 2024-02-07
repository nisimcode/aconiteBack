from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Cluster
from .serializers import ClusterSerializer


@api_view(["GET"])
@permission_classes([AllowAny])
def home(request):
    """
    A view function for the home page.

    Parameters:
        request (Request): The HTTP request object.

    Returns:
        Response: The HTTP response object with a status code of 200 and a JSON payload containing a welcome message.
    """
    return Response(
        status=status.HTTP_200_OK, data={"message": "Welcome to aconite"}
    )


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def clueless(request):
    """
    Retrieves a list of active clusters.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        Response: The HTTP response object containing the serialized data of the active clusters.
    """
    if request.method == "GET":
        object_set = Cluster.objects.filter(is_active=True)
        object_set_serialized = ClusterSerializer(object_set, many=True)
        return Response(status=status.HTTP_200_OK, data=object_set_serialized.data)
