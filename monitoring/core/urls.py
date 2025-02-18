from django.urls import path


import core.views as core_views


app_name = 'core'


urlpatterns = [
    path(
        "host/list/",
        core_views.hosts,
        name='hosts_list'
    ),
    path(
        "host/<int:host_id>/",
        core_views.host,
        name='host'
    ),
    path(
        "host/<int:host_id>/runtime/",
        core_views.host_runtime,
        name='host_runtime'
    ),
    path(
        "host/<int:host_id>/runtime/history/",
        core_views.host_runtime_history,
        name='host_runtime_history'
    ),
    path(
        "ssh/<int:connection_id>/enable/",
        core_views.ssh_connection_enable,
        name='ssh_enable'
    ),
    path(
        "ssh/<int:connection_id>/deploy/",
        core_views.ssh_connection_deploy,
        name='ssh_deploy'
    ),
    path(
        "ssh/<int:connection_id>/disable/",
        core_views.ssh_connection_disable,
        name='ssh_disable'
    ),
]
