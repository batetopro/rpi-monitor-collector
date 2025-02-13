from django.core.management.base import BaseCommand


from network.arp import ArpCollector


class Command(BaseCommand):
    help = "Collects network neighbors information"

    def add_arguments(self, parser):
        pass
        # parser.add_argument("poll_ids", nargs="+", type=int)

    def handle(self, *args, **options):
        arp_collector = ArpCollector()
        arp_collector.collect()
