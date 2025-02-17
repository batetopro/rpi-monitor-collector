import os
import subprocess


from django.conf import settings
from filelock import FileLock


from network.dns import ReverseDnsResolver
from network.models import NeighbourModel


class ArpCollector:
    def save_neighbors(self, arp_records):
        reverse_resolver = ReverseDnsResolver(settings.DNS_SERVERS)

        old_neighbors = dict()
        for entry in NeighbourModel.objects.all():
            old_neighbors[
                '{}@{}'.format(entry.address, entry.interface)
            ] = entry

        new_neighbors = list()

        for record in arp_records:
            key = '{}@{}'.format(record['address'], record['interface'])

            if key in old_neighbors:
                del old_neighbors[key]

            record['status'] = 'connected'
            record['reverse_dns_lookup'] = reverse_resolver.lookup(
                record['address']
            )
            new_neighbors.append(NeighbourModel(**record))

        NeighbourModel.objects.bulk_create(
            new_neighbors,
            update_conflicts=True,
            update_fields=[
                "status", "mask", "physical_address", "type",
                "reverse_dns_lookup"
            ],
            unique_fields=["address", "interface"],
        )

        NeighbourModel.objects.filter(
            pk__in=[
                n.pk for n in old_neighbors.values()
            ]
        ).update(
            status='disconnected',
            mask=None,
            physical_address=None,
            type=None,
            reverse_dns_lookup=None
        )

    def collect(self):
        path = settings.BASE_DIR / 'arp_collect.lock'
        lock = FileLock(path)

        with lock.acquire(timeout=0):
            if os.name == 'nt':
                arp_records = collect_arp_windows()
            else:
                arp_records = collect_arp_linux()

            self.save_neighbors(arp_records)


def collect_arp_windows():
    command = "arp -a"
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=None,
        shell=True
    )

    data = process.communicate()[0].decode()
    result = []

    current_interface = None
    current_mask = None
    for line in data.splitlines():
        if not line:
            continue

        if line.startswith('Interface: '):
            current_interface, current_mask = \
                line[len('Interface: '):].split(' --- ', 1)
            continue

        if line.strip().startswith('Internet Address'):
            continue

        address, physical_address, address_type = line.strip().split()

        if physical_address == 'ff-ff-ff-ff-ff-ff':
            continue

        if physical_address.startswith('01-00-5e-'):
            continue

        result.append({
            'interface': current_interface,
            'mask': current_mask,
            'address': address,
            'physical_address': physical_address,
            'type': address_type,
        })

    return result


def collect_arp_linux():
    command = "arp -e"
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=None,
        shell=True
    )

    data = process.communicate()[0].decode()

    result = []
    for line in data.splitlines():
        if not line.strip():
            continue
        if line.startswith('Address'):
            continue

        parts = line.split()
        if len(parts) == 5:
            record = {
                'interface': parts[4],
                'mask': parts[3],
                'address': parts[0],
                'physical_address': parts[2],
                'type': parts[1],
            }
            result.append(record)

    return result
