import hashlib
import os
import traceback
import uuid


from django.conf import settings
import filelock
from paramiko import AutoAddPolicy, SSHClient


from core.models import SSHConnectionModel


CONNECTION_TIMEOUT = 10


class SSHConnection:
    @property
    def client(self):
        return self._client

    @property
    def connection_id(self):
        return self._connection_id

    @property
    def lock(self):
        return self._lock

    @property
    def virtualenv_path(self):
        return SSHConnectionModel.objects.filter(
            pk=self.connection_id,
            status='enabled'
        ).values_list('monitoring_path', flat=True).first()

    def __init__(self, connection_id):
        self._connection_id = connection_id

        self._client = SSHClient()
        self._client.set_missing_host_key_policy(AutoAddPolicy())

        path = os.path.join(settings.LOCKS_PATH, f'ssh-{connection_id}.lock')
        self._lock = filelock.FileLock(path)

    def connect(self):
        entity = SSHConnectionModel.objects.filter(
            pk=self.connection_id,
            status='enabled'
        ).first()

        if not entity:
            return False

        self.lock.acquire(timeout=0)

        try:
            self.client.connect(
                hostname=entity.username,
                port=entity.port,
                username=entity.port,
                timeout=CONNECTION_TIMEOUT,
                key_filename=entity.ssh_key.identity_file,
            )
        except Exception as ex:
            if settings.DEBUG:
                message = traceback.format_exc()
            else:
                message = str(ex)

            SSHConnectionModel.objects.\
                filter(pk=self.connection_id).\
                update(
                    message=message,
                    session_id=None,
                    state='disconnected'
                )

            self.lock.release()
            return False

        SSHConnectionModel.objects.\
            filter(pk=self.connection_id).\
            update(
                message=None,
                session_id=str(uuid.uuid4()),
                state='connected'
            )

        return True

    def deploy(self):
        self.connect()
        try:
            self.client.exec_command(
                f"cd {self.virtualenv_path} && git pull && ./venv/bin/pip install -r requirements.txt"  # noqa
            )
        finally:
            self.disconnect()

    def disconnect(self):
        self.client.close()

        SSHConnectionModel.objects.\
            filter(pk=self.connection_id).\
            update(
                message=None,
                session_id=None,
                state='disconnected'
            )
        self.lock.release()

    @classmethod
    def test(cls, username, hostname, port, identity_file):
        signature = hashlib.sha1(
            '{}@{}:{}'.format(
                username,
                hostname,
                port
            ).encode()
        ).hexdigest()

        path = os.path.join(
            settings.LOCKS_PATH,
            'ssh-{}.lock'.format(signature)
        )

        lock = filelock.FileLock(path)
        with lock.acquire(timeout=0):
            with SSHClient() as client:
                client.set_missing_host_key_policy(AutoAddPolicy())
                client.connect(
                    hostname=hostname,
                    port=port,
                    username=username,
                    timeout=CONNECTION_TIMEOUT,
                    key_filename=identity_file,
                )

    @classmethod
    def test_connection(cls, connection: SSHConnectionModel):
        try:
            cls.test(
                username=connection.username,
                hostname=connection.hostname,
                port=connection.port,
                identity_file=connection.ssh_key.identity_file
            )
            connection.message = None
        except filelock.Timeout:
            raise
        except Exception as ex:
            if settings.DEBUG:
                connection.message = traceback.format_exc()
            else:
                connection.message = str(ex)

            connection.status = 'disabled'
