from django.core.management.base import BaseCommand


from network.pings import LocalNetworkPings


class Command(BaseCommand):
    help = "Makes ping to all addresses in the machine's local networks."

    def add_arguments(self, parser):
        pass
        # parser.add_argument("poll_ids", nargs="+", type=int)

    def handle(self, *args, **options):
        pings = LocalNetworkPings()
        pings.make()
        print(pings.successful_pings)
