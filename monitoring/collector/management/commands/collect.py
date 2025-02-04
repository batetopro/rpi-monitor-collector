import datetime
import time


from django.core.management.base import BaseCommand
from django.utils.timezone import now


from collector.ssh_collector import SSHCollector
from core.models import DeviceModel, DeviceUsageModel


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

        should_stop = False

        while not should_stop:
            DeviceUsageModel.objects.\
                filter(time_saved__lt=now() - datetime.timedelta(days=2)).\
                delete()

            try:
                time.sleep(10)
            except KeyboardInterrupt:
                should_stop = True
                for collector in collectors.values():
                    collector.stop()

            # Here we need to stop deleted configrations
            # Here we nned to add created configurations
