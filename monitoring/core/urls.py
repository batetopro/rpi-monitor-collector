from django.urls import path


import core.views as core_views


app_name = 'core'


urlpatterns = [
    path(
        "monitoring-diagram/<int:device_id>/",
        core_views.monitoring_diagram,
        name='monitoring_diagram'
    ),
]
