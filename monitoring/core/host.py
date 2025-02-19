import datetime
import json
import os


from django.conf import settings
from django.urls import reverse
from django.utils.timezone import now


from core.models import HostModel
from core.runtime import RuntimeRegistry


class HostRegistry:
    @classmethod
    def get_or_create(cls, connection_id, hostname, up_since,
                      min_cpu_frequency, max_cpu_frequency, total_ram,
                      number_of_cpus, platform_id):

        entity = HostModel.objects.filter(connection_id=connection_id).first()

        if not entity:
            entity = HostModel(connection_id=connection_id)

        entity.hostname = hostname
        entity.up_since = datetime.datetime.fromtimestamp(
            up_since,
            tz=datetime.timezone.utc
        )
        entity.min_cpu_frequency = min_cpu_frequency
        entity.max_cpu_frequency = max_cpu_frequency
        entity.total_ram = total_ram
        entity.number_of_cpus = number_of_cpus
        entity.platform_id = platform_id

        entity.save()

        return entity

    @classmethod
    def get_host(cls, host_id):
        host = HostModel.objects.\
            select_related('platform', 'connection').\
            get(pk=host_id)

        result = {
            'connection': {
                'id': host.connection.pk,
                'state': host.connection.state,
                'status': host.connection.status
            },
            'host_id': host.pk,
            'hostname': host.hostname,
            'max_cpu_frequency': host.max_cpu_frequency,
            'min_cpu_frequency': host.min_cpu_frequency,
            'number_of_cpus': host.number_of_cpus,
            'platform': {
                'model': host.platform.model,
                'os_name': host.platform.os_name,
                'system': host.platform.system,
                'machine': host.platform.machine,
                'processor': host.platform.processor,
                'platform': host.platform.platform,
            },
            'total_ram': host.total_ram,
        }

        return result

    @classmethod
    def get_hosts(cls):
        result = []
        for host in HostModel.objects.\
                select_related('platform', 'connection').\
                order_by(
                    "-connection__status",
                    "connection__state",
                    "hostname"
                ).\
                all():

            runtime = RuntimeRegistry.get_host_runtime(host.pk)
            entry = {
                'host_id': host.pk,
                'change_link': reverse(
                    'management:core_hostmodel_change',
                    args=(host.pk, )
                ),
                'status': host.connection.status,
                'state': host.connection.state,
                'hostname': host.hostname,
                'model': host.platform.model,
                'used_ram': runtime.get('used_ram'),
                'total_ram': host.total_ram,
                'cpu_usage': runtime.get('cpu_usage'),
                'cpu_temperature': runtime.get('cpu_temperature'),
                'total_storage': runtime.get('disk_space_total'),
                'used_storage': runtime.get('disk_space_used'),
            }

            result.append(entry)

        return result

    @classmethod
    def get_runtime(cls, host_id):
        host = HostModel.objects.\
            select_related('connection').\
            filter(pk=host_id).\
            first()

        runtime = RuntimeRegistry.get_host_runtime(host_id)

        result = {
            'host_id': host.pk,
            'hostname': host.hostname,
            'connection': {
                'status': host.connection.status,
                'state': host.connection.state,
            },
            'cpu_frequency': runtime.get('cpu_frequency'),
            'cpu_temperature': runtime.get('cpu_temperature'),
            'cpu_usage': runtime.get('cpu_usage'),
            'disk_io_read_bytes': runtime.get('disk_io_read_bytes'),
            'disk_io_write_bytes': runtime.get('disk_io_write_bytes'),
            'disk_partitions': None,
            'disk_space_available': runtime.get('disk_space_available'),
            'disk_space_total': runtime.get('disk_space_total'),
            'disk_space_used': runtime.get('disk_space_used'),
            'network_io_received_bytes': runtime.get('net_io_bytes_recv'),
            'network_io_sent_bytes': runtime.get('net_io_bytes_sent'),
            'net_io_counters': None,
            'used_ram': runtime.get('used_ram'),
            'used_swap': runtime.get('used_swap'),
            'total_ram': host.total_ram,
            'total_swap': runtime.get('total_swap'),
            'last_seen': runtime.get('timestamp'),
            'time_on_host': runtime.get('time_on_host'),
            'up_since': host.up_since
        }

        disk_partitions = runtime.get('disk_partitions')
        if disk_partitions:
            result['disk_partitions'] = json.loads(disk_partitions)

        net_io_counters = runtime.get('net_io_counters')
        if net_io_counters:
            result['net_io_counters'] = json.loads(net_io_counters)

        if host.up_since:
            result['up_since'] = host.up_since.timestamp()
            if result['time_on_host']:
                result['up_for'] = \
                    round(float(result['time_on_host']) - result['up_since'])
            else:
                result['up_for'] = None
        else:
            result['up_since'] = None
            result['up_for'] = None

        return result

    @classmethod
    def reset_runtime(cls, host_id):
        RuntimeRegistry.clean_host_runtime(host_id)

    @classmethod
    def store_runtime(cls, host_id, cpu_usage, cpu_frequency, cpu_temperature,
                      time_on_host, disk_io_read_bytes, disk_io_write_bytes,
                      disk_space_available, disk_space_used, disk_space_total,
                      disk_partitions,
                      net_io_bytes_recv, net_io_bytes_sent, net_io_counters,
                      used_ram, used_swap, total_swap):

        timestamp = now()

        RuntimeRegistry.store_host_runtime(
            host_id, cpu_usage, cpu_frequency, cpu_temperature,
            time_on_host, disk_io_read_bytes, disk_io_write_bytes,
            disk_space_available, disk_space_used, disk_space_total,
            disk_partitions,
            net_io_bytes_recv, net_io_bytes_sent, net_io_counters,
            used_ram, used_swap, total_swap,
            timestamp
        )

        path = os.path.join(settings.BASE_DIR, 'history')
        if not os.path.exists(path):
            os.makedirs(path)

        path = os.path.join(
            path,
            "host-{}-{}.log".format(host_id, timestamp.strftime("%Y-%m-%d"))
        )

        with open(path, "a") as fp:
            fp.write(
                "{},{},{},{},{},{},{},{}\n".format(
                    timestamp.timestamp(),
                    cpu_temperature,
                    cpu_usage,
                    used_ram,
                    disk_io_read_bytes,
                    disk_io_write_bytes,
                    net_io_bytes_recv,
                    net_io_bytes_sent,
                )
            )
