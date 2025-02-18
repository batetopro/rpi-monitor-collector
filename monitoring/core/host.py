import datetime


from django.urls import reverse
from django.utils.timezone import now


from core.models import HostModel, HostRuntimeModel


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
                'used_ram': host.used_ram,
                'total_ram': host.total_ram,
                'cpu_usage': host.cpu_usage,
                'cpu_temperature': host.cpu_temperature,
                'total_storage': host.disk_space_total,
                'used_storage': host.disk_space_used,
            }

            result.append(entry)

        return result

    @classmethod
    def get_runtime(cls, host_id):
        host = HostModel.objects.\
            select_related('connection').\
            filter(pk=host_id).\
            first()

        result = {
            'host_id': host.pk,
            'hostname': host.hostname,
            'connection': {
                'status': host.connection.status,
                'state': host.connection.state,
            },
            'cpu_frequency': host.cpu_frequency,
            'cpu_temperature': host.cpu_temperature,
            'cpu_usage': host.cpu_usage,
            'disk_io_read_bytes': host.disk_io_read_bytes,
            'disk_io_write_bytes': host.disk_io_write_bytes,
            'disk_partitions': host.disk_partitions,
            'disk_space_available': host.disk_space_available,
            'disk_space_total': host.disk_space_total,
            'disk_space_used': host.disk_space_used,
            'network_io_received_bytes': host.net_io_bytes_recv,
            'network_io_sent_bytes': host.net_io_bytes_sent,
            'used_ram': host.used_ram,
            'used_swap': host.used_swap,
            'total_ram': host.total_ram,
            'total_swap': host.total_swap,
        }

        if host.last_seen:
            result['last_seen'] = host.last_seen.timestamp()
        else:
            result['last_seen'] = None

        if host.time_on_host:
            result['time_on_host'] = host.time_on_host.timestamp()
        else:
            result['time_on_host'] = None

        if host.up_since:
            result['up_since'] = host.up_since.timestamp()
            if host.time_on_host:
                result['up_for'] = \
                    round((host.time_on_host - host.up_since).total_seconds())
            else:
                result['up_for'] = None
        else:
            result['up_since'] = None
            result['up_for'] = None

        return result

    @classmethod
    def reset_runtime(cls, host_id):
        HostModel.objects.filter(pk=host_id).update(
            used_ram=None,
            used_swap=None,
            total_swap=None,
            cpu_frequency=None,
            cpu_temperature=None,
            cpu_usage=None,
            disk_partitions=None,
            disk_space_available=None,
            disk_space_total=None,
            disk_space_used=None,
            disk_io_read_bytes=None,
            disk_io_write_bytes=None,
            net_io_bytes_recv=None,
            net_io_bytes_sent=None,
            up_since=None,
            time_on_host=None,
        )

    @classmethod
    def store_runtime(cls, host_id, cpu_usage, cpu_frequency, cpu_temperature,
                      time_on_host, disk_io_read_bytes, disk_io_write_bytes,
                      disk_space_available, disk_space_used, disk_space_total,
                      disk_partitions, net_io_bytes_recv, net_io_bytes_sent,
                      used_ram, used_swap, total_swap):

        timestamp = now()

        HostModel.objects.filter(pk=host_id).update(
            used_ram=used_ram,
            used_swap=used_swap,
            total_swap=total_swap,
            cpu_frequency=cpu_frequency,
            cpu_temperature=cpu_temperature,
            cpu_usage=cpu_usage,
            disk_partitions=disk_partitions,
            disk_space_available=disk_space_available,
            disk_space_total=disk_space_total,
            disk_space_used=disk_space_used,
            disk_io_read_bytes=disk_io_read_bytes,
            disk_io_write_bytes=disk_io_write_bytes,
            net_io_bytes_recv=net_io_bytes_recv,
            net_io_bytes_sent=net_io_bytes_sent,
            time_on_host=time_on_host,
            last_seen=timestamp
        )

        HostRuntimeModel.objects.create(
            host_id=host_id,
            cpu_temperature=cpu_temperature,
            cpu_usage=cpu_usage,
            used_ram=used_ram,
            disk_io_read_bytes=disk_io_read_bytes,
            disk_io_write_bytes=disk_io_write_bytes,
            net_io_bytes_recv=net_io_bytes_recv,
            net_io_bytes_sent=net_io_bytes_sent,
            time_saved=timestamp,
        )
