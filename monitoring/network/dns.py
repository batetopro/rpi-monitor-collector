from dns import resolver, reversename


class ReverseDnsResolver:
    def __init__(self, dns_servers=[]):
        self._resolver = resolver.Resolver()
        if dns_servers:
            self._resolver.nameservers = dns_servers

    def lookup(self, address):
        try:
            answer = self._resolver.resolve(
                reversename.from_address(address),
                "PTR"
            )
            return answer[0].to_text()
        except Exception:
            return None
