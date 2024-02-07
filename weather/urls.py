from django.urls import path

from . import views

urlpatterns = [
    path("get_weather/", views.get_weather, name="get_weather"),
    path("verify_location/", views.verify_location, name="verify_location"),
    path("add_widget/", views.add_widget, name="add_widget"),
    path("remove_widget/", views.remove_widget, name="remove_widget"),
]
