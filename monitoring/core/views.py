import csv
import datetime
from io import StringIO


from django.contrib.admin.views.decorators import staff_member_required
from django.http.response import HttpResponse, JsonResponse
from django.utils.timezone import now


from core.diagrams import MonitoringDiagram
from core.models import DeviceModel, DeviceUsageModel, HostInfoModel


@staff_member_required
def device_info(request, device_id):
    device = DeviceModel.objects.get(pk=device_id)

    result = {
        'device_id': device_id,
        'status': device.status,
        'cpu_frequency': device.cpu_frequency,
        'cpu_temperature': device.cpu_temperature,
        'cpu_usage': device.cpu_usage,
        'disk_io_read_bytes': device.disk_io_read_bytes,
        'disk_io_write_bytes': device.disk_io_write_bytes,
        'disk_space_available': device.disk_space_available,
        'disk_space_used': device.disk_space_used,
        'error_message': device.message,
        'network_io_received_bytes': device.net_io_bytes_recv,
        'network_io_sent_bytes': device.net_io_bytes_sent,
        'used_ram': device.used_ram,
        'used_swap': device.used_swap,
        'total_swap': device.total_swap,
    }

    if device.time_on_host:
        result['time_on_host'] = device.time_on_host.timestamp()
    else:
        result['time_on_host'] = None

    if device.last_seen:
        result['last_seen'] = device.last_seen.timestamp()
    else:
        result['last_seen'] = None

    if device.up_since:
        result['up_since'] = device.up_since.timestamp()
        if result['last_seen']:
            result['up_for'] = \
                round((device.last_seen - device.up_since).total_seconds())
        else:
            result['up_for'] = None
    else:
        result['up_since'] = None
        result['up_for'] = None

    try:
        host_info = device.host_info
        result['hostname'] = host_info.hostname
        result['total_ram'] = host_info.total_ram
    except HostInfoModel.DoesNotExist:
        result['hostname'] = device.ssh_conf.hostname
        result['total_ram'] = None

    if device.disk_space_available is not None and \
            device.disk_space_used is not None:
        result['disk_space_total'] = \
            device.disk_space_available + device.disk_space_used
    else:
        result['disk_space_total'] = None

    return JsonResponse(result, safe=False)


@staff_member_required
def device_usage(request, device_id):
    # Here a timestamp is optional

    data = DeviceUsageModel.objects.filter(
            device_id=device_id,
            time_saved__gt=now() - datetime.timedelta(minutes=30)
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
def monitoring_diagram(request, device_id):
    diagram = MonitoringDiagram(device_id)
    return HttpResponse(
        content=diagram.plot(),
        content_type='image/svg+xml'
    )
