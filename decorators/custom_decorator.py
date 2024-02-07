from rest_framework.decorators import permission_classes, renderer_classes, parser_classes, \
    authentication_classes
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework_simplejwt.authentication import JWTAuthentication


def custom_decorator(func):
    decorated = permission_classes([IsAuthenticated])(func)
    decorated = renderer_classes([JSONRenderer])(decorated)
    decorated = parser_classes([JSONParser])(decorated)
    decorated = authentication_classes([JWTAuthentication])(decorated)
    return decorated
