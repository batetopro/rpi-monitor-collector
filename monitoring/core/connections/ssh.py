import hashlib
import os
import traceback
import uuid


from django.conf import settings
from django.template import Context, Template
import filelock
from paramiko import AutoAddPolicy, SSHClient, SSHConfig


from core.models import SSHConnectionModel


template_path = os.path.join(
    os.path.dirname(__file__),
    'ssh_conf_template.txt'
)


with open(template_path, "r") as fp:
    conf_template = Template(fp.read())


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

        path = os.path.join(settings.BASE_DIR, f'ssh-{connection_id}.lock')
        self._lock = filelock.FileLock(path)

    def connect(self):
        entity = SSHConnectionModel.objects.filter(
            pk=self.connection_id,
            status='enabled'
        ).first()

        if not entity:
            return False

        conf = self.get_ssh_conf(
            username=entity.username,
            hostname=entity.hostname,
            port=entity.port,
            identity_file=entity.ssh_key.identity_file
        )

        self.lock.acquire(timeout=0)

        try:
            self.client.connect(
                hostname=conf['hostname'],
                port=conf['port'],
                username=conf['user'],
                timeout=float(conf['connecttimeout']),
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
    def get_ssh_conf(cls, username, hostname, port, identity_file):
        rendered: str = conf_template.render(
            Context({
                'username': username,
                'hostname': hostname,
                'port': port,
                'identity_file': identity_file,
            })
        )
        return SSHConfig.from_text(rendered).lookup(hostname)

    @classmethod
    def test(cls, username, hostname, port, identity_file):
        signature = hashlib.sha1(
            '{}@{}:{}'.format(
                username,
                hostname,
                port
            ).encode()
        ).hexdigest()
        path = os.path.join(settings.BASE_DIR, 'ssh-{}.lock'.format(signature))

        lock = filelock.FileLock(path)
        with lock.acquire(timeout=0):
            conf = cls.get_ssh_conf(username, hostname, port, identity_file)

            with SSHClient() as client:
                client.set_missing_host_key_policy(AutoAddPolicy())
                client.connect(
                    hostname=conf['hostname'],
                    port=conf['port'],
                    username=conf['user'],
                    timeout=float(conf['connecttimeout']),
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
