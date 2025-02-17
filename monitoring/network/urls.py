from django.urls import path


import network.views as network_views


app_name = 'network'


urlpatterns = [
    path(
        "make_pings/",
        network_views.make_pings,
        name='make_pings'
    ),
    path(
        "refresh_arp/",
        network_views.refresh_arp,
        name='refresh_arp'
    ),
]
