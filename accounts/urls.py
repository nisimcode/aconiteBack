from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("profile/", views.profile, name="profile"),
    path("profile/activate/", views.activate, name="activate"),
    path("profile/deactivate/", views.deactivate, name="deactivate"),
    path("users/", views.users, name="users"),
    path("token/", views.MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
]
