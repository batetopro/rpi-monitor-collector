from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver


SSH_CONNECTION_STATUS = [
    ("enabled", "Enabled"),
    ("disabled", "Disabled"),
]


class DeviceModel(models.Model):
    class Meta:
        verbose_name = "Device"
        verbose_name_plural = "Devices"

    status = models.CharField(max_length=60)
    message = models.TextField(null=True)
    used_ram = models.PositiveBigIntegerField(null=True)
    used_swap = models.PositiveBigIntegerField(null=True)
    total_swap = models.PositiveBigIntegerField(null=True)
    cpu_frequency = models.FloatField(null=True)
    cpu_temperature = models.PositiveBigIntegerField(null=True)
    cpu_usage = models.PositiveSmallIntegerField(null=True)
    disk_partitions = models.JSONField(null=True)
    disk_space_available = models.PositiveBigIntegerField(null=True)
    disk_space_total = models.PositiveBigIntegerField(null=True)
    disk_space_used = models.PositiveBigIntegerField(null=True)
    disk_io_read_bytes = models.PositiveBigIntegerField(null=True)
    disk_io_write_bytes = models.PositiveBigIntegerField(null=True)
    net_io_bytes_recv = models.PositiveBigIntegerField(null=True)
    net_io_bytes_sent = models.PositiveBigIntegerField(null=True)
    up_since = models.DateTimeField(null=True)
    time_on_host = models.DateTimeField(null=True)
    last_seen = models.DateTimeField(null=True)

    def __str__(self):
        try:
            return self.host_info.hostname
        except HostInfoModel.DoesNotExist:
            return str(self.ssh_conf)


class SSHKeyModel(models.Model):
    class Meta:
        verbose_name = "SSH Key"
        verbose_name_plural = "SSH Keys"

    name = models.CharField(max_length=60, unique=True, null=False)
    identity_file = models.CharField(max_length=2048, null=False)
    public_key = models.TextField(null=False)

    def __str__(self):
        return self.name


class SSHConnectionModel(models.Model):
    class Meta:
        verbose_name = "SSH Connection"
        verbose_name_plural = "SSH Connections"
        unique_together = ("username", "hostname")

    device = models.OneToOneField(
        DeviceModel,
        on_delete=models.CASCADE, null=False, primary_key=True,
        related_name='ssh_conf'
    )
    ssh_key = models.ForeignKey(
        SSHKeyModel, on_delete=models.PROTECT, null=True
    )

    status = models.CharField(max_length=60, null=False, default='enabled',
                              choices=SSH_CONNECTION_STATUS)
    state = models.CharField(max_length=60, null=False, default='disconnected')
    message = models.TextField(null=True)

    hostname = models.CharField(max_length=255, null=False)
    port = models.IntegerField(null=False, default=22)
    username = models.CharField(max_length=255, null=False,
                                default='rpi-monitor')
    monitoring_path = models.CharField(max_length=2048, null=False,
                                       default='/home/rpi-monitor/rpi-monitor')

    def __str__(self):
        return f'{self.username}@{self.hostname}:{self.port}'

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):

        if self.status == 'enabled':
            from core.connections.ssh import SSHConnection
            SSHConnection.test_connection(self)

        return super().save(force_insert, force_update, using, update_fields)


class HostInfoModel(models.Model):
    class Meta:
        verbose_name = "Host Infromation"
        verbose_name_plural = "Host Infromations"

    device = models.OneToOneField(
        DeviceModel,
        on_delete=models.CASCADE, null=False, primary_key=True,
        related_name='host_info'
    )
    hostname = models.CharField(max_length=255, null=False)
    model = models.CharField(max_length=255, null=False)
    os_name = models.CharField(max_length=255, null=False)
    system = models.CharField(max_length=255, null=False)
    machine = models.CharField(max_length=60, null=False)
    processor = models.CharField(max_length=60, null=False)
    platform = models.TextField(null=False)
    max_cpu_frequency = models.FloatField(null=True)
    number_of_cpus = models.PositiveBigIntegerField(null=False)
    total_ram = models.PositiveBigIntegerField(null=False)


class DeviceUsageModel(models.Model):
    class Meta:
        verbose_name = "Device Usage"
        verbose_name_plural = "Device Usage"

    device = models.ForeignKey(
        DeviceModel, on_delete=models.CASCADE, null=False
    )

    cpu_frequency = models.PositiveBigIntegerField(null=True)
    cpu_temperature = models.PositiveBigIntegerField(null=True)
    cpu_usage = models.PositiveBigIntegerField(null=False)
    used_ram = models.PositiveBigIntegerField(null=False)
    disk_io_read_bytes = models.PositiveBigIntegerField(null=True)
    disk_io_write_bytes = models.PositiveBigIntegerField(null=True)
    net_io_bytes_recv = models.PositiveBigIntegerField(null=True)
    net_io_bytes_sent = models.PositiveBigIntegerField(null=True)
    current_date = models.DateTimeField(null=False)
    time_saved = models.DateTimeField(
        null=False, auto_now_add=True, db_index=True
    )


@receiver(pre_save, sender=SSHConnectionModel)
def set_connection_device(sender, instance, *args, **kwargs):
    if instance.device_id is None:
        device = DeviceModel.objects.create(status='installing')
        instance.device_id = device.id
