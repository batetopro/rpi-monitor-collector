import time
import threading


from core.connections.ssh import SSHConnection
from core.receiver import CollectorReceiver
from core.scheduler import Scheduler


class SSHCollector:
    @property
    def channel(self):
        if self._channel is None:
            transport = self.connection.client.get_transport()
            if transport.is_active():
                self._channel = transport.open_session()
        return self._channel

    @property
    def connection_id(self):
        return self._connection_id

    @property
    def connection(self):
        return self._connection

    @property
    def receiver(self):
        if self._receiver is None:
            self._receiver = CollectorReceiver(self.connection_id)
        return self._receiver

    @property
    def scheduler(self):
        return self._scheduler

    def __init__(self, connection_id):
        self._channel = None
        self._connection_id = connection_id
        self._connection = SSHConnection(connection_id)
        self._receiver = CollectorReceiver(self.connection_id)
        self._scheduler = Scheduler(self.receiver._callbacks.keys())
        self._should_stop = False
        self._thread = None

    def collect(self):
        while not self._should_stop:
            if not self.connection.connect():
                time.sleep(60)
                continue

            virtualenv_path = self.connection.virtualenv_path
            if not virtualenv_path:
                break

            try:
                self.channel.exec_command(
                    f'cd {virtualenv_path} && ./venv/bin/flask chat'
                )
            except Exception:
                break

            self.scheduler.add_task("platform", 0)
            self.scheduler.add_task("host", 1)
            self.scheduler.add_task("net_interfaces", 2)
            self.scheduler.add_task("runtime", 3)

            while not self._should_stop:
                timestamp = time.time()
                queries = self.scheduler.get_awaiting(timestamp)

                while queries and not self._should_stop:
                    query = queries.pop(0)
                    data = self.send_and_read(query)
                    self.receiver.receive(query, data)

                    if query == "net_interfaces":
                        self.scheduler.add_task(
                            "net_interfaces",
                            timestamp + 60.0
                        )

                    if query == "runtime":
                        self.scheduler.add_task(
                            "runtime",
                            timestamp + 1.0
                        )

        if self._channel is not None:
            self.channel.close()
            self._channel = None

        self.connection.disconnect()
        self.receiver.disconnect()

    def run(self):
        self._thread = threading.Thread(target=self.collect, daemon=True)
        self._thread.start()

    def send_and_read(self, query):
        while not self.channel.send_ready():
            time.sleep(.1)
            continue

        self.channel.send(query + '\n')

        while not self.channel.recv_ready():
            time.sleep(.1)
            continue

        data = bytearray()
        resp = self.channel.recv(64)
        length, resp = resp.split(b'\n', 1)
        data.extend(resp)
        length = int(length) - 64

        while length > 0:
            resp = self.channel.recv(2048)
            length -= 2048
            data.extend(resp)

        return data.decode()

    def stop(self):
        self._should_stop = True
        self._thread.join()
