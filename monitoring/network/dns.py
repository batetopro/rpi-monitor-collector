import os


from dns import resolver, reversename


class ReverseDnsResolver:
    def __init__(self):
        self._resolver = resolver.Resolver()

        if os.name == 'nt':
            hosts_path = r'C:\Windows\System32\drivers\etc\hosts'
        else:
            hosts_path = '/etc/hosts'

        self._hosts = self.read_hosts(hosts_path)

    def lookup(self, address):
        if address in self._hosts:
            return self._hosts[address]

        try:
            answer = self._resolver.resolve(
                reversename.from_address(address),
                "PTR"
            )
            return answer[0].to_text()
        except Exception:
            return None

    def read_hosts(self, path):
        result = dict()
        if not os.path.exists(path):
            return result

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

                    if address not in result:
                        result[address] = domain

        return result
