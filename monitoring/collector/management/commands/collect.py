import datetime
import time


from django.core.management.base import BaseCommand
from django.utils.timezone import now


from collector.ssh_collector import SSHCollector
from core.models import SSHConnectionModel


from core.models import HostRuntimeModel


class Command(BaseCommand):
    help = "Collects monitoring information"

    def add_arguments(self, parser):
        pass
        # parser.add_argument("poll_ids", nargs="+", type=int)

    def clean_old_usage(self):
        HostRuntimeModel.objects.\
            filter(time_saved__lt=now() - datetime.timedelta(days=2)).\
            delete()

    def get_enabled_connections(self):
        return SSHConnectionModel.objects.filter(status='enabled')

    def handle(self, *args, **options):
        collectors = dict()

        for conn in self.get_enabled_connections():
            collector = SSHCollector(conn.pk)
            collectors[conn.pk] = collector
            collector.run()

        while True:
            try:
                self.clean_old_usage()

                time.sleep(10)

                disabled = set(collectors.keys())
                newly_enabled = []

                for connection in self.get_enabled_connections():
                    if connection.pk not in collectors:
                        newly_enabled.append(connection.pk)
                    elif connection.pk in disabled:
                        disabled.remove(connection.pk)

                for connection_id in disabled:
                    collectors[connection_id].stop()
                    del collectors[connection_id]

                for connection_id in newly_enabled:
                    collector = SSHCollector(connection_id)
                    collectors[connection_id] = collector
                    collector.run()

            except KeyboardInterrupt:
                for collector in collectors.values():
                    collector.stop()

                break
