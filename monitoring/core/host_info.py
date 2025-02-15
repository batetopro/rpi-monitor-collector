from django.utils.timezone import now


from core.models import DeviceModel, DeviceUsageModel, HostInfoModel


class HostInfo:
    @property
    def device(self):
        return self._device

    @property
    def entry(self):
        return self._entry

    def __init__(self, device: DeviceModel):
        self._device = device
        self._entry = None

    def fetch(self):
        self._entry = self.device.host_info
        return self.entry

    def update_info(self, hostname, model, os_name, system, machine, processor,
                    platform, up_since, max_cpu_frequence, total_ram,
                    number_of_cpus):

        DeviceModel.objects.filter(id=self.device.id).update(
            message=None,
            status='connected',
            up_since=up_since
        )

        entry = HostInfoModel.objects.filter(device_id=self.device.id).first()

        if not entry:
            entry = HostInfoModel(device_id=self.device.id)

        entry.hostname = hostname
        entry.model = model
        entry.os_name = os_name
        entry.system = system
        entry.machine = machine
        entry.processor = processor
        entry.platform = platform
        entry.max_cpu_frequency = max_cpu_frequence
        entry.total_ram = total_ram
        entry.number_of_cpus = number_of_cpus

        entry.save()

        self._entry = entry

        return self.entry

    def update_usage(self, cpu_usage, cpu_frequency, cpu_temperature,
                     disk_space_available, disk_space_used, disk_space_total,
                     disk_io_read_bytes, disk_io_write_bytes,
                     net_io_bytes_recv, net_io_bytes_sent,
                     used_ram, used_swap, total_swap, current_date):

        DeviceModel.objects.filter(id=self.device.id).update(
            cpu_usage=cpu_usage,
            cpu_frequency=cpu_frequency,
            cpu_temperature=cpu_temperature,
            disk_space_available=disk_space_available,
            disk_space_total=disk_space_total,
            disk_space_used=disk_space_used,
            disk_io_read_bytes=disk_io_read_bytes,
            disk_io_write_bytes=disk_io_write_bytes,
            net_io_bytes_recv=net_io_bytes_recv,
            net_io_bytes_sent=net_io_bytes_sent,
            used_ram=used_ram,
            used_swap=used_swap,
            total_swap=total_swap,
            time_on_host=current_date,
            last_seen=now(),
        )

        DeviceUsageModel.objects.create(
            device_id=self.device.id,
            cpu_frequency=cpu_frequency,
            cpu_temperature=cpu_temperature,
            cpu_usage=cpu_usage,
            used_ram=used_ram,
            disk_io_read_bytes=disk_io_read_bytes,
            disk_io_write_bytes=disk_io_write_bytes,
            net_io_bytes_recv=net_io_bytes_recv,
            net_io_bytes_sent=net_io_bytes_sent,
            current_date=current_date
        )
