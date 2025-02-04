import time


from django.core.management.base import BaseCommand


from collector.ssh_collector import SSHCollector
from core.models import DeviceModel


class Command(BaseCommand):
    help = "Collects monitoring information"

    def add_arguments(self, parser):
        pass
        # parser.add_argument("poll_ids", nargs="+", type=int)

    def get_device_collector(self, device):
        return SSHCollector(device)

    def get_devices(self):
        result = []
        for device in DeviceModel.objects.all():
            result.append(device)
        return result

    def handle(self, *args, **options):
        collectors = dict()

        for device in self.get_devices():
            collectors[device.id] = self.get_device_collector(device)
            collectors[device.id].run()

        while True:
            time.sleep(10)
