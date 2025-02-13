from django.db import models


class NeighbourModel(models.Model):
    class Meta:
        verbose_name = "Neighbour"
        verbose_name_plural = "Neighbors"
        unique_together = ('address', 'interface', )

    address = models.CharField(max_length=64, null=False)
    interface = models.CharField(max_length=64, null=False)
    status = models.CharField(max_length=20, null=False,
                              default='disconnected')
    mask = models.CharField(max_length=8, null=True)
    physical_address = models.CharField(max_length=64, null=True)
    type = models.CharField(max_length=32, null=True)

    def __str__(self):
        return "{}@{}".format(self.address, self.interface)


class DnsRecordModel(models.Model):
    class Meta:
        verbose_name = "DNS Record"
        verbose_name_plural = "DNS Records"

    neighbour = models.ForeignKey(
        NeighbourModel, null=True, on_delete=models.SET_NULL
    )
    address = models.CharField(max_length=64, null=False)
    domain = models.CharField(max_length=255, null=False)

    def __str__(self):
        return "{}@{}".format(self.domain, self.address)
