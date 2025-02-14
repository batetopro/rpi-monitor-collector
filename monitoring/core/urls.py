from django.urls import path


import core.views as core_views


app_name = 'core'


urlpatterns = [
    path(
        "device/<int:device_id>/info/",
        core_views.device_info,
        name='device_info'
    ),
    path(
        "device/<int:device_id>/usage/",
        core_views.device_usage,
        name='device_usage'
    ),
]
