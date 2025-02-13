from django.core.management.base import BaseCommand


from network.dns import DnsCollector


class Command(BaseCommand):
    help = "Collects DNS configuration"

    def add_arguments(self, parser):
        pass
        # parser.add_argument("poll_ids", nargs="+", type=int)

    def handle(self, *args, **options):
        dns_collector = DnsCollector()
        dns_collector.collect()
