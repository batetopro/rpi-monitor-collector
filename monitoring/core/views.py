import csv
import datetime
from io import StringIO


from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.urls import reverse
from django.http.response import HttpResponse, HttpResponseRedirect, \
    JsonResponse
from django.utils.timezone import now


from core.host import HostRegistry
from core.models import HostRuntimeModel, SSHConnectionModel
from core.connections.ssh import SSHConnection


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
def host_runtime(request, host_id):
    return JsonResponse(
        HostRegistry.get_runtime(host_id),
        safe=False
    )


@staff_member_required
def host_runtime_history(request, host_id):
    # Here a timestamp is optional

    data = HostRuntimeModel.objects.filter(
            host_id=host_id,
            time_saved__gt=now() - datetime.timedelta(minutes=10)
        ).\
        values_list(
            'time_saved',
            'cpu_usage',
            'cpu_temperature',
            'used_ram',
            'disk_io_read_bytes',
            'disk_io_write_bytes',
            'net_io_bytes_recv',
            'net_io_bytes_sent',
        ).\
        order_by('time_saved')

    result = []

    for row in data:
        result.append((
            row[0].timestamp(),
            row[1],
            row[2],
            row[3],
            row[4],
            row[5],
            row[6],
            row[7]
        ))

    with StringIO() as buf:
        writer = csv.writer(buf)
        writer.writerows(result)
        return HttpResponse(
            content=buf.getvalue().strip(),
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
