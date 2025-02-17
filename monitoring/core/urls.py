from django.urls import path


import core.views as core_views


app_name = 'core'


urlpatterns = [
    path(
        "device/list/",
        core_views.devices,
        name='devices_list'
    ),
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
    path(
        "ssh/<int:connection_id>/enable/",
        core_views.ssh_connection_enable,
        name='ssh_enable'
    ),
    path(
        "ssh/<int:connection_id>/disable/",
        core_views.ssh_connection_disable,
        name='ssh_disable'
    ),
]
