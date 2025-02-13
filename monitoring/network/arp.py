import ipaddress
import os
import subprocess
import threading


from django.conf import settings


from network.models import NeighbourModel


class ArpCollector:
    def make_pings(self):
        number_of_ip_buckets = 8
        ip_buckets = []
        ip_index = 0
        ping_threads = []

        for k in range(number_of_ip_buckets):
            ip_buckets.append(list())

        for network_address in settings.SCAN_NETWORKS:
            network = ipaddress.IPv4Network(network_address)
            for ip in network:
                if ip.is_multicast or ip == network.broadcast_address:
                    continue

                ip_buckets[ip_index % number_of_ip_buckets].append(str(ip))
                ip_index += 1

        for k in range(number_of_ip_buckets):
            ping_threads.append(
                threading.Thread(
                    target=ping_ip_addresses,
                    args=(ip_buckets[k])
                )
            )

        for k in range(number_of_ip_buckets):
            ping_threads[k].start()

        for k in range(number_of_ip_buckets):
            ping_threads[k].join()

    def save_neighbors(self, arp_records):
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
            new_neighbors.append(NeighbourModel(**record))

        NeighbourModel.objects.bulk_create(
            new_neighbors,
            update_conflicts=True,
            update_fields=["status", "mask", "physical_address", "type"],
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
            type=None
        )

    def collect(self):
        self.make_pings()

        if os.name == 'nt':
            arp_records = collect_arp_windows()
        else:
            arp_records = collect_arp_linux()

        self.save_neighbors(arp_records)


def collect_arp_windows():
    data = os.popen('arp -a').read()
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


def ping_ip_addresses(*ip_addresses):
    if os.name == 'nt':
        for ip in ip_addresses:
            os.popen('ping -n 1 {}'.format(ip))
    else:
        for ip in ip_addresses:
            os.popen('ping -c 1 {}'.format(ip))
