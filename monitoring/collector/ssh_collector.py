import time
import threading


from core.receiver import CollectorReceiver
from core.connections.ssh import SSHConnection


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

    def __init__(self, connection_id):
        self._channel = None
        self._connection_id = connection_id
        self._connection = SSHConnection(connection_id)
        self._receiver = None
        self._should_stop = False
        self._thread = None
        self._queries = []

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

            self._queries.append("platform")
            self._queries.append("host")
            self._queries.append("runtime")

            while not self._should_stop:
                if not self._queries:
                    continue

                query = self._queries.pop(0)
                data = self.send_and_read(query)
                self.receiver.receive(query, data)

                if query == "runtime":
                    time.sleep(.1)
                    self._queries.append("runtime")

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

        # This should read first block, get content length,
        # read blocks after that
        data = self.channel.recv(2048)

        return data.decode()

    def stop(self):
        self._should_stop = True
        self._thread.join()
