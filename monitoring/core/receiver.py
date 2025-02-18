import datetime
import json


from django.conf import settings


from core.host import HostRegistry
from core.platform import PlatformRegistry


class CollectorReceiver:
    def __init__(self, connection_id):
        self._connection_id = connection_id

        self._callbacks = {
            "platform": self.receive_platform,
            "host": self.receive_host,
            "runtime": self.receive_runtime,
        }

        self._host_id = None
        self._platform_id = None

    def disconnect(self):
        HostRegistry.reset_runtime(self._host_id)

    def receive(self, query, data):
        if query in self._callbacks:
            self._callbacks[query](data)

            if settings.DEBUG:
                print(
                    "{} {} {}".format(
                        datetime.datetime.now(), self._host_id, query
                    )
                )

    def receive_host(self, data):
        data = json.loads(data)

        host = HostRegistry.get_or_create(
            connection_id=self._connection_id,
            hostname=data["hostname"],
            up_since=data["up_since"],
            min_cpu_frequency=data["min_cpu_frequency"],
            max_cpu_frequency=data["max_cpu_frequency"],
            total_ram=data["total_ram"],
            number_of_cpus=data["number_of_cpus"],
            platform_id=self._platform_id
        )

        self._host_id = host.pk

    def receive_runtime(self, data):
        data = json.loads(data)

        HostRegistry.store_runtime(
            host_id=self._host_id,
            cpu_usage=data['cpu_usage'],
            cpu_frequency=data['cpu_frequency'],
            cpu_temperature=data['cpu_temperature'],
            time_on_host=datetime.datetime.fromtimestamp(
                data['current_date'],
                tz=datetime.timezone.utc
            ),
            disk_io_read_bytes=data['disk_io_read_bytes'],
            disk_io_write_bytes=data['disk_io_write_bytes'],
            disk_space_available=data['disk_space_available'],
            disk_space_used=data['disk_space_used'],
            disk_space_total=data['disk_space_total'],
            disk_partitions=data['disk_partitions'],
            net_io_bytes_recv=data['net_io_bytes_recv'],
            net_io_bytes_sent=data['net_io_bytes_sent'],
            used_ram=data['ram'],
            used_swap=data['swap_used'],
            total_swap=data['swap_total']
        )

        # TODO: Here -> schedule the next runtime collection

    def receive_platform(self, data):
        data = json.loads(data)

        platform = PlatformRegistry.get_or_create(
            model=data["model"],
            os_name=data["os_name"],
            system=data["system"],
            machine=data["machine"],
            processor=data["processor"],
            platform=data["platform"]
        )

        self._platform_id = platform.pk
