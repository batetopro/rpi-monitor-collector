import os


from network.models import DnsRecordModel


class DnsCollector:
    def collect(self):
        if os.name == 'nt':
            hosts = r'C:\Windows\System32\drivers\etc\hosts'
        else:
            hosts = '/etc/hosts.d'

        hosts_records = read_hosts(hosts)
        self.save_hosts_records(hosts_records)

    def save_hosts_records(self, hosts_records):
        old_records = dict()
        for entry in DnsRecordModel.objects.all():
            old_records[
                '{}@{}'.format(entry.domain, entry.address)
            ] = entry

        new_records = list()
        for record in hosts_records:
            key = '{}@{}'.format(record['domain'], record['address'])

            if key in old_records:
                del old_records[key]
                continue

            new_records.append(record)

        for neighbor in new_records:
            DnsRecordModel.objects.create(**neighbor)

        DnsRecordModel.objects.filter(
            pk__in=[
                n.pk for n in old_records.values()
            ]
        ).delete()


def read_hosts(path):
    result = []
    if not os.path.exists(path):
        return []

    with open(path, 'r') as fp:
        for line in fp.readlines():
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('ï»¿#'):
                continue

            parts = line.split(maxsplit=1)

            if len(parts) == 1:
                continue

            address, domains = parts

            for domain in domains.split():
                if not domain:
                    continue

                result.append({
                    'address': address,
                    'domain': domain
                })

    return result
