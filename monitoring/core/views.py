import datetime
import os


from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.urls import reverse
from django.http.response import HttpResponse, HttpResponseRedirect, \
    JsonResponse
from django.utils.timezone import now


from core.connections.ssh import SSHConnection
from core.host import HostRegistry
from core.models import SSHConnectionModel
from core.network_interface import NetworkInterfaceRegistry


@staff_member_required
def hosts(request):
    result = {
        'hosts': HostRegistry.get_hosts(),
    }

    return JsonResponse(result, safe=False)


@staff_member_required
def host(request, host_id):
    result = HostRegistry.get_host(host_id)
    return JsonResponse(result, safe=False)


@staff_member_required
def host_net_interfaces(request, host_id):
    result = NetworkInterfaceRegistry.get_network_interfaces(host_id)
    return JsonResponse(result, safe=False)


@staff_member_required
def host_runtime(request, host_id):
    return JsonResponse(
        HostRegistry.get_runtime(host_id),
        safe=False
    )


@staff_member_required
def host_runtime_history(request, host_id):
    # Here a timestamp is optional

    current_time = now()
    since = (current_time - datetime.timedelta(minutes=10)).timestamp()

    path = os.path.join(
        settings.BASE_DIR,
        'history',
        "host-{}-{}.log".format(host_id, current_time.strftime("%Y-%m-%d"))
    )

    if not os.path.exists(path):
        return HttpResponse(
            content='',
            content_type='text/csv'
        )

    rows = []
    with open(path, "r") as fp:
        for line in fp.readlines():
            timestamp, _ = line.split(',', 1)
            timestamp = float(timestamp)
            if timestamp < since:
                continue
            rows.append(line)

    return HttpResponse(
        content=''.join(rows),
        content_type='text/csv'
    )


@staff_member_required
def ssh_connection_disable(request, connection_id):
    SSHConnectionModel.objects.filter(pk=connection_id).\
        update(status='disabled')
    return HttpResponseRedirect(request.META["HTTP_REFERER"])


@staff_member_required
def ssh_connection_enable(request, connection_id):
    connection = SSHConnectionModel.objects.get(pk=connection_id)
    connection.status = 'enabled'
    connection.save()

    if connection.status != 'enabled':
        messages.add_message(
            request,
            messages.ERROR,
            "SSH connection could not be enabled."
        )
        return HttpResponseRedirect(
            reverse(
                'management:core_sshconnectionmodel_change',
                args=(connection_id, )
            )
        )

    return HttpResponseRedirect(request.META["HTTP_REFERER"])


@staff_member_required
def ssh_connection_deploy(request, connection_id):
    connection = SSHConnection(connection_id)
    connection.deploy()
    return HttpResponseRedirect(request.META["HTTP_REFERER"])
