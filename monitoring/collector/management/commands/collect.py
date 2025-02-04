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

        while True:
            try:
                DeviceUsageModel.objects.\
                    filter(time_saved__lt=now() - datetime.timedelta(days=2)).\
                    delete()

                time.sleep(10)

                deleted_devices = set(collectors.keys())
                new_devices = []

                for device in self.get_devices():
                    if device.id not in collectors:
                        new_devices.append(device)
                    elif device.id in deleted_devices:
                        deleted_devices.remove(device.id)

                for device in new_devices:
                    collectors[device.id] = self.get_device_collector(device)
                    collectors[device.id].run()

                for device_id in deleted_devices:
                    collectors[device_id].stop()
                    del collectors[device_id]

            except KeyboardInterrupt:
                for collector in collectors.values():
                    collector.stop()
                break
