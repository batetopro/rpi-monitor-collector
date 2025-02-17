import ipaddress
from socket import AddressFamily
import threading


from django.conf import settings
from filelock import FileLock
import psutil
from pythonping import ping


class LocalNetworkPings:
    @property
    def successful_pings(self):
        return self._successful_pings

    def __init__(self):
        self._successful_pings = None

    def make(self, number_of_buckets=8):
        path = settings.BASE_DIR / 'make_pings.lock'
        lock = FileLock(path)
        with lock.acquire(timeout=0):
            self._successful_pings = []

            buckets = self.prepare_buckets(number_of_buckets)

            ping_threads = []
            for k in range(number_of_buckets):
                ping_threads.append(
                    threading.Thread(
                        target=self.ping_ip_addresses,
                        args=(buckets[k]),
                        daemon=True
                    )
                )

            for k in range(number_of_buckets):
                ping_threads[k].start()

            for k in range(number_of_buckets):
                ping_threads[k].join()

    def get_local_networks(self):
        result = set()

        up_adapters = set()
        for name, info in psutil.net_if_stats().items():
            if info.isup:
                up_adapters.add(name)

        for name, addresses in psutil.net_if_addrs().items():
            if name not in up_adapters:
                continue

            for address in addresses:
                if address.family != AddressFamily.AF_INET:
                    continue

                a = ipaddress.IPv4Address(address.address)
                if a.is_loopback or address.netmask is None:
                    continue

                network = ipaddress.IPv4Network(
                    "{}/{}".format(address.address, address.netmask),
                    strict=False
                )
                result.add(str(network))

        return result

    def ping_ip_addresses(self, *ips):
        for ip in ips:
            result = ping(ip, timeout=2, count=1)
            if result.success():
                self.successful_pings.append(ip)

    def prepare_buckets(self, number_of_buckets=8):
        local_networks = self.get_local_networks()

        scan_networks = settings.SCAN_NETWORKS
        if scan_networks:
            local_networks = local_networks & set(scan_networks)

        buckets = []
        for _ in range(number_of_buckets):
            buckets.append(list())

        for network_address in local_networks:
            network = ipaddress.IPv4Network(network_address)

            for idx, address in enumerate(network):
                if address.is_multicast or \
                        address == network.broadcast_address:
                    continue

                buckets[idx % number_of_buckets].append(str(address))

        return buckets
