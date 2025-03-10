from django.db import models


SSH_CONNECTION_STATUS = [
    ("enabled", "Enabled"),
    ("disabled", "Disabled"),
]


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

    ssh_key = models.ForeignKey(
        SSHKeyModel, on_delete=models.PROTECT, null=True
    )

    status = models.CharField(max_length=60, null=False, default='enabled',
                              choices=SSH_CONNECTION_STATUS)
    state = models.CharField(max_length=60, null=False, default='disconnected')
    session_id = models.CharField(max_length=40, null=True)

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


class PlatformModel(models.Model):
    class Meta:
        verbose_name = "Platform"
        verbose_name_plural = "Platforms"

    model = models.CharField(max_length=255, null=False)
    os_name = models.CharField(max_length=255, null=False)
    system = models.CharField(max_length=255, null=False)
    machine = models.CharField(max_length=60, null=False)
    processor = models.CharField(max_length=60, null=False)
    platform = models.TextField(null=False)
    signature = models.CharField(max_length=64, null=False, unique=True)


class HostModel(models.Model):
    class Meta:
        verbose_name = "Host"
        verbose_name_plural = "Hosts"

    connection = models.OneToOneField(
        SSHConnectionModel, on_delete=models.CASCADE, null=False,
        related_name='host'
    )
    platform = models.ForeignKey(
        PlatformModel, on_delete=models.PROTECT, null=False
    )

    hostname = models.CharField(max_length=255, null=True)
    total_ram = models.PositiveBigIntegerField(null=True)
    number_of_cpus = models.PositiveSmallIntegerField(null=False)
    min_cpu_frequency = models.FloatField(null=True)
    max_cpu_frequency = models.FloatField(null=True)
    up_since = models.DateTimeField(null=True)

    def __str__(self):
        if self.hostname is None:
            return self.connection.hostname
        return self.hostname


class NetworkInterfaceModel(models.Model):
    class Meta:
        verbose_name = "Network Interface"
        verbose_name_plural = "Network Interfaces"
        unique_together = ('host', 'name', )

    host = models.ForeignKey(
        HostModel, on_delete=models.CASCADE, null=False
    )
    name = models.CharField(max_length=64, null=False)
    isup = models.BooleanField(null=True)
    duplex = models.CharField(max_length=20, null=True)
    speed = models.PositiveIntegerField(null=True)
    mtu = models.PositiveIntegerField(null=True)
    ip4_address = models.CharField(max_length=40, null=True)
    ip6_address = models.CharField(max_length=120, null=True)
    addresses = models.JSONField(null=True)

    def __str__(self):
        return f'{self.name}@{self.host.hostname}'
