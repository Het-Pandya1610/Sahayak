from django.urls import path

from .views import (
    get_schemes,
    get_scheme_details
)


urlpatterns = [

    path(
        '',
        get_schemes
    ),

    path(
        '<str:id>/',
        get_scheme_details
    ),
]